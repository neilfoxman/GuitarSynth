
import pyaudio
import time
import numpy as np
from subprocess import PIPE, Popen, run
import shlex
import mido
import wiringpi

import notedetect
from soxCommands import *

# Initialize wiringPi Button on Pin #6:
wiringpi.wiringPiSetupGpio()
wiringpi.pinMode(6,0)

# Set main vars:
FORMAT = np.int16
CHANNELS = 1
RATE = 192000
FRAMES_BYPASS = 2**9
FRAMES_SYNTH = 2**13
PERIOD = 1.0/float(RATE)

# Mappings for convenience:
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
    """ Generates SoX formatted I/O information """
    return ' '.join([
        '-t ' + ENCODINGS_MAPPING[FORMAT],
        '-r ' + str(RATE),
        '-c ' + str(CHANNELS),
        '-',
    ])

def wire(BYPASS, SOX):
    run(["aconnect", "-x"]) # Remove outstanding audio connections

    rate = RATE
    frames_bypass = FRAMES_BYPASS
    frames_synth = FRAMES_SYNTH

    # NoteDector class:
    nd = notedetect.NoteDetector(frames_synth, PERIOD)
    nd.noteDetectionThreshold = 0.18 * len(nd.usableBins) * 32767

    # PyAudio streaming device:
    p = pyaudio.PyAudio()

    # Open MIDO port for sending MIDI data:
    outport = mido.open_output('Midi Through:Midi Through Port-0 14:0')

    # Generate SoX command for chosen effect(s) (soxCommands.py):
    CMD_PREFIX = shlex.split(
                ' '.join(['sox','-N','-V1', numpyArrayToCMD(), numpyArrayToCMD(),
                    OVERDRIVE_CMD]),
                posix=False,)

    def callback(in_data, frame_count, time_info, status):
        """ Each iteration of PyAudio's stream has an audio callback which we intercept """

        if BYPASS: # Pass audio unchanged
            return(in_data, pyaudio.paContinue)

        # Convert audio data to given format:
        stdin = np.frombuffer(in_data, dtype=FORMAT)
        
        if SOX: # Pass audio after SoX updates
            stdout, stderr = Popen(
                CMD_PREFIX, stdin=PIPE, stdout=PIPE, stderr=PIPE
                ).communicate(stdin.tobytes(order='F'))
            return (stdout, pyaudio.paContinue)
        
        # Run FFT and detect MIDI notes played:
        nd.runFFT(stdin)
        startNotes, stopNotes = nd.detectNotes()
        
        # Generate SINE tone based on notes played:
        voice = np.zeros(frames_synth)
        for note in nd.currentNotes:
            f = notedetect.midiNoteToFrequency(note)
            voice = (5000*np.sin(2*np.pi*np.arange(frames_synth)*f/rate)).astype(FORMAT).tobytes()
            pass
        
        # Send note_on messages to chosen synthesizer using MIDO:
        if(len(startNotes) > 0):
            for noteNum in startNotes:
                outport.send(mido.Message('note_on', note=noteNum))
                print("Started:",noteNum, notedetect.noteToLetter(noteNum))
        
        # Send note_off messages using MIDO:
        if(len(stopNotes) > 0):
            for noteNum in stopNotes:
                outport.send(mido.Message('note_off', note=noteNum))
        
        return (voice, pyaudio.paContinue)

    # Open PyAudio stream:
    stream = p.open(format=ENCODINGS_MAPPING_PYAUDIO[FORMAT],
                    channels=CHANNELS,
                    rate=rate,
                    input=True,
                    output=True,
                    frames_per_buffer=frames_bypass,
                    stream_callback=callback)

    # Start the stream and keep it running while waiting for button presses:
    stream.start_stream()
    fsynth = None # Is fluidsynth running?
    event_count = 0 # How many button presses have we seen?

    while stream.is_active():

        presentVal = wiringpi.digitalRead(6)

        if presentVal == 0: # Button press!
            event_count += 1

            if event_count % 3 == 0: # Bypass mode
                print("Bypassing...")
                BYPASS = True
                SOX = False
                
                # Stop the stream:
                stream.stop_stream()
                stream.close()
                
                # Kill fluidsynth if it is running:
                if fsynth: fsynth.kill()
                
                # Start a new stream:
                stream = p.open(format=ENCODINGS_MAPPING_PYAUDIO[FORMAT],
                    channels=CHANNELS,
                    rate=rate,
                    input=True,
                    output=True,
                    frames_per_buffer=frames_bypass,
                    stream_callback=callback)
                stream.start_stream()
                
            elif event_count % 3 == 1: # Effect mode
                print("Overdriving...")
                BYPASS = False
                SOX = True
                
                # Stop the stream:
                stream.stop_stream()
                stream.close()
                
                # Start a new stream:
                stream = p.open(format=ENCODINGS_MAPPING_PYAUDIO[FORMAT],
                    channels=CHANNELS,
                    rate=rate,
                    input=True,
                    output=True,
                    frames_per_buffer=frames_synth,
                    stream_callback=callback)
                stream.start_stream()
                
            else: # Synth mode
                print("Synth...")
                BYPASS = False
                SOX = False
                
                # Stop the stream:
                stream.stop_stream()
                stream.close()
                
                # Open fluidsynth (using subprocess.Popen)
                fsynth = Popen(["fluidsynth", "--audio-driver=alsa",
                                "--gain", "3", "/usr/share/sounds/sf2/FluidR3_GM.sf2"])

                # Once fluidsynth is open, we read the audio port (takes 1-5s to open):
                fluid_synth_port = ""
                while(fluid_synth_port == ""):
                    try:
                        acon_out = run(["aconnect", "-o"], capture_output=True)
                        acon_out = str(acon_out).split(' ')
                        fluid_synth_port = int(acon_out[acon_out.index("'FLUID") - 1][:-1])
                    except:
                        time.sleep(.5)
                
                # Connect our MIDO port to the fluidsynth port:
                run(["aconnect", "14:0", str(fluid_synth_port) + ":0"])
                
                # Open a new stream:
                stream = p.open(format=ENCODINGS_MAPPING_PYAUDIO[FORMAT],
                    channels=CHANNELS,
                    rate=rate,
                    input=True,
                    output=False,
                    frames_per_buffer=frames_synth,
                    stream_callback=callback)
                stream.start_stream()
                
        time.sleep(0.3) # Discrete time steps help to register clean button presses

    stream.stop_stream()
    stream.close()
    p.terminate()

if __name__ == "__main__":
    wire(True, False)
