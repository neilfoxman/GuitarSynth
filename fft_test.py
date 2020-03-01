import notedetect
import numpy as np
import matplotlib.pyplot as plt

fs = 44100.0
Ts = 1/fs

t0 = 0
tf = 0.1

f1 = 440.0
f2 = 261.6

t = np.arange(t0, tf, Ts)

sig1 = np.sin(2*np.pi*f1*t)
sig2 = np.sin(2*np.pi*f2*t)

figure, axis = plt.subplots(4,1)
plt.subplots_adjust(hspace=1)

axis[0].set_title('First sin wave')
axis[0].plot(t,sig1)
axis[0].set_xlabel('Time')
axis[0].set_ylabel('Amplitude')

axis[1].set_title('Second sin wave')
axis[1].plot(t,sig2)
axis[1].set_xlabel('Time')
axis[1].set_ylabel('Amplitude')

sig3 = sig1 + sig2

axis[2].set_title('Sin wave with multiple frequencies')
axis[2].plot(t,sig3)
axis[2].set_xlabel('Time')
axis[2].set_ylabel('Amplitude')

# Prep note detector
nd = notedetect.NoteDetector(len(sig3), Ts)

# Run fft
transformed = nd.runFFT(sig3)

# Run note detection
startNotes, stopNotes = nd.detectNotes()



axis[3].set_title('Fourier transform')
axis[3].plot(nd.farray,transformed)
axis[3].set_xlabel('Frequency')
axis[3].set_ylabel('Amplitude')

#plt.show()



# Check that notes are started
print("~~~~~First sample")
print("Notes started:")
for noteNum in startNotes:
    print(noteNum)

# No notes should be stopped
print("Notes stopped:")
for noteNum in stopNotes:
    print(noteNum)




# Now assume a new sample has come in but first frequency is not playing
sig3 = np.sin(2*np.pi*f2*t)

# Run fft
transformed = nd.runFFT(sig3)

# Run note detection
startNotes, stopNotes = nd.detectNotes()

# No notes should be started
print("~~~~~Second sample")
print("Notes started:")
for noteNum in startNotes:
    print(noteNum)

# One note should be stopped
print("Notes stopped:")
for noteNum in stopNotes:
    print(noteNum)
