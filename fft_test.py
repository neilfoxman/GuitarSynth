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

trans1 = np.fft.fft(sig3)/len(sig3) # Normalize
trans2 = trans1[range(int(len(sig3)/2))] # Exclude above fNyquist

tpCount = len(sig3)
values = np.arange(int(tpCount/2))
T = tpCount/fs
f = values/T

axis[3].set_title('Fourier transform')
axis[3].plot(f,abs(trans2))
axis[3].set_xlabel('Frequency')
axis[3].set_ylabel('Amplitude')

plt.show()
