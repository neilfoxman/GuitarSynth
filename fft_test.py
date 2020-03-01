# https://pythontic.com/visualization/signals/fouriertransform_fft
import numpy as np
import matplotlib.pyplot as plt
#from scipy.fftpack import rfft, fftfreq
import math

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



# trans1 = np.fft.rfft(sig3)#/len(sig3) # Normalize (
# f1 = np.fft.fftfreq(len(sig3), Ts)
# #trans1 = rfft(sig3)#/len(sig3) # Normalize (
# #f1 = fftfreq(len(sig3), Ts)
# print("Input signal is ", len(sig3), " long")
# print("Output of fft() is ", len(trans1), " long")
# print(len(f1), " frequency bins created")
# print("fft result is of type ", trans1.dtype)

# Empty note used for error checking
#noNote = Note(-1)

def frequencyToMidiNote(f):
    if(f <=0):
        return 0
    else:
        return 12.0*math.log(float(f)/27.5,2)+21

def midiNoteToFrequency(midiNote):
    return 27.5*2.0**((float(midiNote)-21.0)/12.0)

class Note:
    def __init__(self, midiNum):
        self.midiNum = float(midiNum)
        self.frequency = midiNoteToFrequency(self.midiNum)
        #self.frequency_lowerBound = midiNoteToFrequency(self.midiNum - 0.5)
        #self.frequency_upperBound = midiNoteToFrequency(self.midiNum + 0.5)
        self.isPlaying = False
        
#     def isWithinBounds(self, inspectedFrequency):
#         if inspectedFrequency > self.frequency_lowerBound:
#             if inspectedFrequency < self.frequency_upperBound:
#                 return True
#         return False
    
def mapFrequenciesToNotes(fArray):
    # Create list of notes
    noteList = []
    
    # Assign each frequency a midi note and add it to the list
    for f in farray:
        midiNum = frequencyToMidiNote(f)
        noteList.append(int(round(midiNum)))
        
    # By now you should have a list of notes the same size as the farray
    # Convert the list into an array
    noteArray = np.array(noteList)
    return noteArray
    
# def findCorrespondingNote(inspectedFrequency, arrayOfNotes):
#     for note in arrayofNotes:
#         if note.isWithinBounds(inspectedFrequency):
#             return note
#     return noNote

def generatePlayableNoteArray(numNotes):
    noteList = []
    for i in range(numNotes):
        noteList.append(Note(i))
    noteArr = np.array(noteList)
    return noteArr

def generateFrequencyArray(signalLength, samplePeriod):
    # Fng frequencies that would be used given a signal sample length and sample period
    farray_all = np.fft.fftfreq(signalLength, samplePeriod)
    
    # Create dummy signal and runn fft to get appropriate length of transformation
    dummySig = np.zeros(signalLength)
    dummyTransformed = np.fft.rfft(dummySig)
    
    # Exclude redundant frequencies due to discrete transform
    usableBins = range(len(dummyTransformed) - 1) # last bin is negative frequency
    farray = farray_all[usableBins]
    
    # Debug
    print("Dummy Input signal is ", len(dummySig), " long")
    print("Dummy Output of fft() is ", len(dummyTransformed), " long")
    print(len(farray), " frequency bins created by fftfreq")
    print("Asserting that there are ", len(usableBins), " usable bins")
    
    return farray, usableBins

def runFFT(signal, rangeOfUsableBins):
    # Transform array into frequency domain
    transformed_all = np.fft.rfft(signal)#/len(sig3) # Normalize (
    
    # Exclude redundant frequencies due to discrete transform
    transformed = abs(transformed_all[rangeOfUsableBins])
    
    # Debug
    print("Input signal is ", len(dummySig), " long")
    print("Output of fft() is ", len(dummyTransformed), " long")
    print("fft result is of type ", transformed.dtype)

    return transformed

def detectNote(farr, transarr, detectionThreshold):#, frequencyToNoteMap, currentNotes, previousNotes):
    # Detect frequencies above threshold
    f = 0 # start inspecting frequencies in farray
    while idx < len(farr):
        # If the frequency inspected is higher than threshold
        if transarr[idx] > detectionThreshold:
            # Find corresponding midi note number
            midiNote = frequencyToNoteMap[idx]
            
            # Set note to playing
            currentNotes[midiNote].isPlaying = True
            return
            
            
            
        
    
    # Convert frequencies to midi note numbers

# Create an array of all the playable notes (127 of them)
masterNoteArr = generatePlayableNoteArray(127)

# Generate array of frequencies corresponding to the fft bins when it runs
signalLength = len(sig3)
farray, usableBins = generateFrequencyArray(signalLength, Ts)

# Assign each frequency to a Midi Note
noteMap = mapFrequenciesToNotes(farray)

# Run fft
transformed = runFFT(sig3,usableBins)

# Run note detection
noteDetectionThreshold = 0.5


# Checking that frequency amplitude is aligned to correct frequency
# finspect = range(39,42) # 4 Hz
# finspect = range(69,72) # 7 Hz
# print(f2[finspect])
# print(abs(trans2[finspect]))


axis[3].set_title('Fourier transform')
axis[3].plot(frequencies,abs(transformed))
axis[3].set_xlabel('Frequency')
axis[3].set_ylabel('Amplitude')

#plt.show()
