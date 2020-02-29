# https://pythontic.com/visualization/signals/fouriertransform_fft
import numpy as np
import matplotlib.pyplot as plt

fs = 100.0
Ts = 1/fs

t0 = 0
tf = 10

f1 = 4
f2 = 7

t = np.arange(t0, tf, Ts)

sig1 = np.sin(2*np.pi*f1*t)
sig2 = np.sin(2*np.pi*f2*t)

figure, axis = plt.subplots(4,1)
plt.subplots_adjust(hspace=1)

axis[0].set_title('Sin wave f = 4 Hz')
axis[0].plot(t,sig1)
axis[0].set_xlabel('Time')
axis[0].set_ylabel('Amplitude')

axis[1].set_title('Sin wave f = 7 Hz')
axis[1].plot(t,sig2)
axis[1].set_xlabel('Time')
axis[1].set_ylabel('Amplitude')

sig3 = sig1 + sig2

axis[2].set_title('Sin wave with multiple frequencies')
axis[2].plot(t,sig3)
axis[2].set_xlabel('Time')
axis[2].set_ylabel('Amplitude')

trans1 = np.fft.fft(sig3)#/len(sig3) # Normalize (
f1 = np.fft.fftfreq(len(sig3), Ts)
print("Input signal is ", len(sig3), " long")
print("Output of fft() is ", len(trans1), " long")
print(len(f1), " frequency bins created")
print("fft result is of type ", trans1.dtype)

# Exclude redundant frequencies in discrete transform
usablebins = range(int(len(sig3)/2))
trans2 = trans1[usablebins]
f2 = f1[usablebins]


axis[3].set_title('Fourier transform')
axis[3].plot(f2,abs(trans2))
axis[3].set_xlabel('Frequency')
axis[3].set_ylabel('Amplitude')

plt.show()
