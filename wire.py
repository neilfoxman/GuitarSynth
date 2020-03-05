
import pyaudio
import time
import numpy as np
from subprocess import PIPE, Popen, run
import shlex
import notedetect
import mido
from soxCommands import *
import wiringpi

wiringpi.wiringPiSetupGpio()
wiringpi.pinMode(6,0)


FORMAT = np.int16
CHANNELS = 1
RATE = 192000
FRAMES = 2**9
PERIOD = 1.0/float(RATE)

ENCODINGS_MAPPING = {
    np.int8: 's8',
    np.int16: 's16',
    np.float32: 'f32',
}

ENCODINGS_MAPPING_PYAUDIO = {
    np.int8: pyaudio.paInt8,
    np.int16: pyaudio.paInt16,
    np.float32: pyaudio.paFloat32,
}

def numpyArrayToCMD():
            return ' '.join([
                '-t ' + ENCODINGS_MAPPING[FORMAT],
                '-r ' + str(RATE),
                '-c ' + str(CHANNELS),
                '-',
            ])

def wire(BYPASS, SOX):
    # INIT #
    #BYPASS = False # Callback will pass the audio without modulating
    #SOX = False # Callback will call SoX commands (BYPASS overrides)
    

    # MAIN CLASSES #
    rate = RATE
    frames_bypass = FRAMES
    frames_synth = 2**13
    nd = notedetect.NoteDetector(frames_synth, PERIOD)
    nd.noteDetectionThreshold = 0.18 * len(nd.usableBins) * 32767
    p = pyaudio.PyAudio()

    # MIDO PORT #
    outport = mido.open_output('Midi Through:Midi Through Port-0 14:0')

    # SOX CMD #
    CMD_PREFIX = shlex.split(
                ' '.join(['sox','-N','-V1', numpyArrayToCMD(), numpyArrayToCMD(),
                    OVERDRIVE_CMD]),
                posix=False,)

    # CALLBACK #
    def callback(in_data, frame_count, time_info, status):

        if BYPASS: # Pass audio unchanged
            return(in_data, pyaudio.paContinue)

        stdin = np.frombuffer(in_data, dtype=FORMAT)
        
        if SOX: # Pass audio after SoX updates
            stdout, stderr = Popen(
                CMD_PREFIX, stdin=PIPE, stdout=PIPE, stderr=PIPE
                ).communicate(stdin.tobytes(order='F'))
            return (stdout, pyaudio.paContinue)
        
        # Synth
        nd.runFFT(stdin)
        startNotes, stopNotes = nd.detectNotes()
        
        voice = np.zeros(frames_synth)
        for note in nd.currentNotes:
            f = notedetect.midiNoteToFrequency(note)
            voice = (5000*np.sin(2*np.pi*np.arange(frames_synth)*f/rate)).astype(FORMAT).tobytes()
            pass
        
        if(len(startNotes) > 0):
            for noteNum in startNotes:
                outport.send(mido.Message('note_on', note=noteNum))
                print("Started:",noteNum, notedetect.noteToLetter(noteNum))
        
        if(len(stopNotes) > 0):
            for noteNum in stopNotes:
                outport.send(mido.Message('note_off', note=noteNum))
        
        return (voice, pyaudio.paContinue)


    stream = p.open(format=ENCODINGS_MAPPING_PYAUDIO[FORMAT],
                    channels=CHANNELS,
                    rate=rate,
                    input=True,
                    output=True,
                    frames_per_buffer=frames_bypass,
                    stream_callback=callback)

    stream.start_stream()
    fsynth = None
    event_count = 0
    while stream.is_active():
        presentVal = wiringpi.digitalRead(6)
        if presentVal == 0:
            print("Press detected...")
            event_count += 1
            if event_count % 3 == 0:
                print("Bypassing...")
                BYPASS = True
                SOX = False
                
                stream.stop_stream()
                stream.close()
                
                if fsynth: fsynth.kill()
                
                stream = p.open(format=ENCODINGS_MAPPING_PYAUDIO[FORMAT],
                    channels=CHANNELS,
                    rate=rate,
                    input=True,
                    output=True,
                    frames_per_buffer=frames_bypass,
                    stream_callback=callback)
                stream.start_stream()
                
            elif event_count % 3 == 1:
                print("Overdriving...")
                BYPASS = False
                SOX = True
                
                stream.stop_stream()
                stream.close()
                
                stream = p.open(format=ENCODINGS_MAPPING_PYAUDIO[FORMAT],
                    channels=CHANNELS,
                    rate=rate,
                    input=True,
                    output=True,
                    frames_per_buffer=frames_synth,
                    stream_callback=callback)
                stream.start_stream()
                
            else:
                print("Synth...")
                BYPASS = False
                SOX = False
                
                stream.stop_stream()
                stream.close()
                
                fsynth = Popen(["fluidsynth", "--audio-driver=alsa",
                                "--gain", "3", "/usr/share/sounds/sf2/FluidR3_GM.sf2"])
                
                stream = p.open(format=ENCODINGS_MAPPING_PYAUDIO[FORMAT],
                    channels=CHANNELS,
                    rate=rate,
                    input=True,
                    output=False,
                    frames_per_buffer=frames_synth,
                    stream_callback=callback)
                stream.start_stream()
                
        time.sleep(0.3)

    stream.stop_stream()
    stream.close()
    p.terminate()

if __name__ == "__main__":
    wire(True, False)