import pyaudio
import struct
import numpy as np
# import matplotlib.pyplot as plt
import wave



# Adapting from:
# https://jfraj.github.io/2015/06/17/recording_audio.html
# https://slides.com/jeancruypenynck/introduction-to-pyaudio/embed#/10
# https://www.youtube.com/watch?v=AShHJdSIxkY


p = pyaudio.PyAudio()
print("\n~~~~~~~~~~\n")

FRAME_RATE = 44100 # sample rate
FORMAT = pyaudio.paInt16 # 16 bit int
CHANNELS = 1 # I guess this is for mono sounds
DEVICE_INDEX = 2
FRAMES_PERBUFF = 256 # number of frames per buffer, was 2048 originally

# def callback(in_data, frame_count, time_info, status):
    # data = wf.readframes(frame_count)
    # return (data, pyaudio.paContinue)

stream = p.open(rate=FRAME_RATE,
				format=FORMAT,
                channels=CHANNELS,
                input=True,
                output=True,
                input_device_index=DEVICE_INDEX,
                output_device_index=DEVICE_INDEX,
                frames_per_buffer=FRAMES_PERBUFF,
				stream_callback=None)
                
                
RECORD_SECONDS = 10
nchunks = int(RECORD_SECONDS * FRAME_RATE / FRAMES_PERBUFF)
frames = []
for i in range(0, nchunks):
    data = stream.read(FRAMES_PERBUFF)
    frames.append(data) # 2 bytes(16 bits) per channel
print("* done recording")
stream.stop_stream()
stream.close()
p.terminate()

print(frames)



wf = wave.open('recorded_audio.wav', 'wb')
wf.setnchannels(CHANNELS)
wf.setsampwidth(p.get_sample_size(FORMAT))
wf.setframerate(FRAME_RATE)
wf.writeframes(b''.join(frames))
wf.close()
