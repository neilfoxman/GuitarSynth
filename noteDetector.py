# https://www.youtube.com/watch?v=AShHJdSIxkY
import pyaudio
import struct
import numpy as np
import matplotlib.pyplot as plt
import wave
import sys

CHUNK = 1024

# Round up chunk size to power of two to maximize fft efficiency
# http://www.ece.northwestern.edu/local-apps/matlabhelp/techdoc/ref/nextpow2.html
CHUNK = 2**math.ceil(math.log(CHUNK,2))

if len(sys.argv) < 2:
    print("Plays a wave file.\n\nUsage: %s filename.wav" % sys.argv[0])
    sys.exit(-1)

wf = wave.open(sys.argv[1], 'rb')

# instantiate PyAudio (1)
p = pyaudio.PyAudio()
print("\nBegin stream ~~~~~~~~~~\n")





    

# open stream (2)
stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                channels=wf.getnchannels(),
                rate=wf.getframerate(),
                output=True)



# read data
data = wf.readframes(CHUNK)

# play stream (3)
while len(data) > 0:
    stream.write(data)
    data = wf.readframes(CHUNK)

# stop stream (4)
stream.stop_stream()
stream.close()

# close PyAudio (5)
p.terminate()
