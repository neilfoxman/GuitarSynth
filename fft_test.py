# https://pythontic.com/visualization/signals/fouriertransform_fft
import numpy as np
import matplotlib.pyplot as plt
#from scipy.fftpack import rfft, fftfreq
import math

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



# trans1 = np.fft.rfft(sig3)#/len(sig3) # Normalize (
# f1 = np.fft.fftfreq(len(sig3), Ts)
# #trans1 = rfft(sig3)#/len(sig3) # Normalize (
# #f1 = fftfreq(len(sig3), Ts)
# print("Input signal is ", len(sig3), " long")
# print("Output of fft() is ", len(trans1), " long")
# print(len(f1), " frequency bins created")
# print("fft result is of type ", trans1.dtype)

def frequencyToMidiNote(f):
	return 12.0*math.log(float(fspike)/27.5,2)+21

def midiNoteToFrequency(midiNote):
	return 27.5*2.0**((float(midiNote)-21.0)/12.0)

def detectNote(signal, lenSignal, samplePeriod, detectionThreshold):
    # Transform array into frequency domain
    transformed = np.fft.rfft(signal)#/len(sig3) # Normalize (
    farray = np.fft.fftfreq(lenSignal, samplePeriod)
    print("Input signal is ", len(signal), " long")
    print("Output of fft() is ", len(transformed), " long")
    print(len(farray), " frequency bins created")
    print("fft result is of type ", transformed.dtype)
    
    # Exclude redundant frequencies due to discrete transform
	usablebins = range(len(trans1) - 1) # last bin is negative frequency
	trans2 = trans1[usablebins]
	f2 = f1[usablebins]
    
    # Detect frequencies above threshold
    # TODO
    
    # Convert frequencies to midi note numbers
    
    
    
    return transformed, farray
    
trans1, f1 = detectNote(sig3, len(sig3), Ts, 0)




# Checking that frequency amplitude is aligned to correct frequency
# finspect = range(39,42) # 4 Hz
# finspect = range(69,72) # 7 Hz
# print(f2[finspect])
# print(abs(trans2[finspect]))


axis[3].set_title('Fourier transform')
axis[3].plot(f2,abs(trans2))
axis[3].set_xlabel('Frequency')
axis[3].set_ylabel('Amplitude')

plt.show()
