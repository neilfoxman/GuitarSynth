import pyaudio
import time
import numpy as np
from subprocess import PIPE, Popen
import shlex
import notedetect
import mido
from soxCommands import *

# INIT #
BYPASS = False # Callback will pass the audio without modulating
SOX = False # Callback will call SoX commands (BYPASS overrides)
FORMAT = np.int16
CHANNELS = 1
RATE = 44100
FRAMES = 2**9 if (BYPASS or SOX) else 2**11
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

# MAIN CLASSES #
nd = notedetect.NoteDetector(FRAMES, PERIOD)
nd.noteDetectionThreshold = 0.12 * len(nd.usableBins) * 32767
p = pyaudio.PyAudio()

# MIDO PORT #
outport = mido.open_output('Midi Through:Midi Through Port-0 14:0')

# SOX CMD #
if SOX:
    def numpyArrayToCMD():
        return ' '.join([
            '-t ' + ENCODINGS_MAPPING[FORMAT],
            '-r ' + str(RATE),
            '-c ' + str(CHANNELS),
            '-',
        ])

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
    
    voice = np.zeros(FRAMES)
    for note in nd.currentNotes:
        f = notedetect.midiNoteToFrequency(note)
        voice = (4000*np.sin(2*np.pi*np.arange(FRAMES)*f/RATE)).astype(FORMAT).tobytes()
        pass
    
    if(len(startNotes) > 0):
        for noteNum in startNotes:
            outport.send(mido.Message('note_on', note=noteNum))
            print("Started:",noteNum, notedetect.noteToLetter(noteNum))
    
    if(len(stopNotes) > 0):
        for noteNum in stopNotes:
            outport.send(mido.Message('note_off', note=noteNum))
            print("Stopped:",noteNum, notedetect.noteToLetter(noteNum))
    
    return (voice, pyaudio.paContinue)

stream = p.open(format=ENCODINGS_MAPPING_PYAUDIO[FORMAT],
                channels=CHANNELS,
                rate=RATE,
                input=True,
                output=True,
                frames_per_buffer=FRAMES,
                stream_callback=callback)

stream.start_stream()

while stream.is_active():
    time.sleep(0.1)

stream.stop_stream()
stream.close()

p.terminate()
