import pyaudio
import time
import numpy as np
from subprocess import PIPE, Popen
import shlex
import notedetect

FORMAT = np.int16
CHANNELS = 1
RATE = 44100

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

BYPASS = False # Callback will pass the audio without modulating
OVERDRIVE_CMD = "overdrive 10 10" # gain, color
CHORUS_CMD = "chorus 0.7 0.9 55 0.4 0.25 2 -t" # gain-in gain-out delay decay speed depth sin/triangle
DELAY_CMD = "delay 0.5" # seconds
FLANGER_CMD = "flanger"
PHASE_CMD = "phaser 0.89 0.85 1 0.24 2 -t" # gain-in gain-out delay decay speed sin/triangle
PITCH_CMD = "pitch 10" # cents
REVERB_CMD = "reverb -w" # wet (vs dry)
TEMOLO_CMD = "tremolo 20 40" # speed depth

framesPerBuffer = 2**11
samplingPeriod = 1.0/float(RATE)
nd = notedetect.NoteDetector(framesPerBuffer, samplingPeriod)
nd.noteDetectionThreshold = 0.1*len(nd.usableBins)*32767

p = pyaudio.PyAudio()

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

def callback(in_data, frame_count, time_info, status):

    if BYPASS: 
        return(in_data, pyaudio.paContinue)

    stdin = np.frombuffer(in_data, dtype=FORMAT)
    #print(list(stdin))
    #stdout, stderr = Popen(CMD_PREFIX, stdin=PIPE, stdout=PIPE, stderr=PIPE).communicate(stdin.tobytes(order='F'))
    
    nd.runFFT(stdin)
    
    # Run note detection
    startNotes, stopNotes = nd.detectNotes()
    # [0, 0, 62, 62, 62, 0, 0, 64, 64, 64] -> byte array
    
    
    voice = np.zeros(framesPerBuffer)
    t = np.arange(framesPerBuffer)
    for note in nd.currentNotes:
        f = notedetect.midiNoteToFrequency(note)
        #voice += 50*np.sin(2*np.pi*f*t)
        voice = (2000*np.sin(2*np.pi*np.arange(framesPerBuffer)*f/RATE)).astype(FORMAT).tobytes()
        pass
    
    
    
    # No notes should be started
    if(len(startNotes) > 0):
        for noteNum in startNotes:
            print("Started:",noteNum)
    
    # One note should be stopped
    if(len(stopNotes) > 0):
        for noteNum in stopNotes:
            print("Stopped:",noteNum)
    
    return (voice, pyaudio.paContinue)
    #return (stdin, pyaudio.paStop)

stream = p.open(format=ENCODINGS_MAPPING_PYAUDIO[FORMAT],
                channels=CHANNELS,
                rate=RATE,
                input=True,
                output=True,
                frames_per_buffer=framesPerBuffer,
                stream_callback=callback)

stream.start_stream()

while stream.is_active():
    time.sleep(0.1)

stream.stop_stream()
stream.close()

p.terminate()
