import pyaudio
import time
import numpy as np
from subprocess import PIPE, Popen
import shlex

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

BYPASS = True # Callback will pass the audio without modulating
OVERDRIVE_CMD = "overdrive 10 10" # gain, color
    

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
    #print("In:", type(in_data), type(in_data[0]), in_data)
    #print("Frame count:", frame_count)
    #print("Time info:", time_info)
    #print("Status:", status)
    
    stdin = np.frombuffer(in_data, dtype=FORMAT)
    stdout, stderr = Popen(CMD_PREFIX, stdin=PIPE, stdout=PIPE, stderr=PIPE).communicate(stdin.tobytes(order='F'))
    
    return (stdout, pyaudio.paContinue)

stream = p.open(format=ENCODINGS_MAPPING_PYAUDIO[FORMAT],
                channels=CHANNELS,
                rate=RATE,
                input=True,
                output=True,
                frames_per_buffer=1056,
                stream_callback=callback)

stream.start_stream()

while stream.is_active():
    time.sleep(0.1)

stream.stop_stream()
stream.close()

p.terminate()
