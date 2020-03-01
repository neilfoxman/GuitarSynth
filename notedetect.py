# Reference Material:
# https://pythontic.com/visualization/signals/fouriertransform_fft
import numpy as np
#from scipy.fftpack import rfft, fftfreq
import math




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
        self.isPlaying = False
        self.lowestNoteIdx = -1


class NoteDetector:    
    def __init__(self, signalLength, samplingPeriod):
        print("~~~~~ Started Note Detector")
        self.signalLength = signalLength
        self.samplingPeriod = samplingPeriod
        
        # Check for fft optimization
        # From http://www.ece.northwestern.edu/local-apps/matlabhelp/techdoc/ref/nextpow2.html
        opt = 2**math.ceil(math.log(self.signalLength,2))
        if(self.signalLength != opt):
            print("*** Current num samples is", signalLength, ". Increase to", opt, "for maximum efficiency")
        
        # Generate array of frequencies corresponding to the bins when fft runs
        # Do this in the beginning so it doesn't have to run each cycle
        self.farray, self.usableBins = self.generateFrequencyArray(self.signalLength, self.samplingPeriod)
        self.numUsableBins = len(self.usableBins)
        
        # Assign each frequency to a Midi Note
        self.noteMap = self.mapFrequenciesToNotes(self.farray)

        # Create an array of all the playable notes
        self.masterNoteArray = self.generateMasterNoteArray(self.noteMap)
        self.numPlayableNotes = len(self.masterNoteArray)

        # Set note detection threshold default
        # Output of fft() is scaled by len(sig), compensate for that here
        # One could also normalize the fft output, but that takes more time in the loop
        self.noteDetectionThreshold = 0.5*len(self.usableBins)
        
        # Keep track of notes playing
        self.currentNotes = []
        self.previousNotes = []
        
        # Keep track of notes started and ending
        self.startNotes = []
        self.stopNotes = []


    def generateFrequencyArray(self, signalLength, samplePeriod):
        # Find frequencies that would be used given a signal sample length and sample period
        farray_all = np.fft.fftfreq(signalLength, samplePeriod)
        
        # Create dummy signal and runn fft to get appropriate length of transformation
        dummySig = np.zeros(signalLength)
        dummyTransformed = np.fft.rfft(dummySig)
        
        # Exclude redundant frequencies due to discrete transform
        usableBins = range(len(dummyTransformed) - 1) # last bin is negative frequency
        farray = farray_all[usableBins]
        
        # Debug
#         print("Dummy Input signal is ", len(dummySig), " long")
#         print("Dummy Output of fft() is ", len(dummyTransformed), " long")
#         print("Asserting that there are ", len(usableBins), " usable bins")
        print("Frequency array is ", len(farray), " long")
        
        return farray, usableBins
        
    def mapFrequenciesToNotes(self, fArray):
        # Create list of notes
        noteList = []
        
        # Assign each frequency a midi note and add it to the list
        for f in fArray:
            midiNum = frequencyToMidiNote(f)
            noteList.append(int(round(midiNum)))
            
        # By now you should have a list of notes the same size as the farray
        # Convert the list into an array
        noteArray = np.array(noteList)
        return noteArray

    # Create an array of notes where the index corresponds to the midi number
    def generateMasterNoteArray(self, noteMap):
        masterNoteList = []

        # Find maximum note number used (last entry in noteMap)
        maxNote = noteMap[self.numUsableBins - 1]
        
        # Create an array of note objects up to and including that number
        for noteNumber in range(maxNote + 1):
            masterNoteList.append(Note(noteNumber))
            

        # Convert to array
        masterNoteArray = np.array(masterNoteList)
        
        # Once one spectrum value is found that is higher than the threshold,
        # we set that note to playing and we skip inspecting the remaining frequencies
        # To implement this, we need the lowest possible index of the frequency bins
        # that corresponds to each note.
        
        # Inspect notes in noteMap starting from highest frequency
        inspectedIdx = self.numUsableBins - 1 # last entry on noteMap
        lowestIdx = inspectedIdx # variable to store lowest index found for this note number
        while inspectedIdx >=0:
            # Corresponding note number
            inspectedNote = noteMap[inspectedIdx]
            
            
            if inspectedIdx == 0:
                # If we are inspecting the last element, that is the lowest possible index
                # corresponding to that note
                lowestIdx = 0
            elif(noteMap[inspectedIdx - 1] != noteMap[inspectedIdx]):
                # If the next lower note number is different from inspected note, then
                # the inspected note has the lowest possible index for that note
                lowestIdx = inspectedIdx
                
            # Save the lowest Idx found so far
            masterNoteArray[inspectedNote].lowestNoteIdx = lowestIdx
            
#             # Debug
#             print("inspectedIdx=", inspectedIdx,
#                   "inspectedNote=", inspectedNote,
#                   "midiNum=",masterNoteArray[inspectedNote].midiNum,
#                   "lowestNoteIdx=",masterNoteArray[inspectedNote].lowestNoteIdx
#                   )
            
            # Start looking at the next lower index
            inspectedIdx -= 1
        
        
        
#         # Debug - Check that all notes have correct minimum index
#         print("After Assignment:")
#         note = masterNoteArray[0]
#         print("midiNum=",note.midiNum,
#             "lowestNoteIdx=",note.lowestNoteIdx,
#             "noteMap[note.lowestNoteIdx]=", noteMap[note.lowestNoteIdx],
#             "noteMap[note.lowestNoteIdx+1]=", noteMap[note.lowestNoteIdx+1]
#             )
#         for note in masterNoteArray:
#             if(note.lowestNoteIdx > 0):
#                 print("midiNum=",note.midiNum,
#                       "lowestNoteIdx=",note.lowestNoteIdx,
#                       "noteMap[note.lowestNoteIdx-1]=", noteMap[note.lowestNoteIdx-1],
#                       "noteMap[note.lowestNoteIdx]=", noteMap[note.lowestNoteIdx],
#                       "noteMap[note.lowestNoteIdx+1]=", noteMap[note.lowestNoteIdx+1]
#                       )


        
        # Diagnostics - The bins generated by fft are spaced out in a linear scale while
        # acoustic notes are spaced out on a logarithmic scale (see conversion functions).
        # This means that the lower midi notes may not have corresponding
        # frequency bins after fft().  This section detects the lowest sequential frequency.

        # Count down from highest frequency
        for idx in reversed(range(self.numUsableBins)):
            # If we have counted down past zero than no notes are skipped
            if(idx-1 < 0):
                print("All midi notes can be played!")
            
            # If the note lower than the inspected one is not exactly one lower,
            elif((noteMap[idx-1] != noteMap[idx]) and
                 (noteMap[idx-1] != noteMap[idx] - 1)):
                # Then we found our lower bound of sequential notes
                
#                 print(noteMap[idx-1], " is not sequential with ", noteMap[idx])
                print("Lowest sequential playable note is ", noteMap[idx])
                break
        
        return masterNoteArray
        


    def runFFT(self, signal):
        # Transform array into frequency domain
        transformed_all = np.fft.rfft(signal)#/len(sig3) # Normalize (
        
        # Exclude redundant frequencies due to discrete transform
        transformed = abs(transformed_all[self.usableBins])
        
#         # Debug
#         print("Input signal is ", len(signal), " long")
#         print("Output of fft() is ", len(transformed_all), " long")
#         print("Usable fft() output is ", len(transformed), " long")
#         print("fft result is of type ", transformed.dtype)
        
        # Save transformed variable
        self.transformed = transformed

        return transformed

    def detectNotes(self):
        # Reset note trackers
        self.previousNotes = self.currentNotes
        self.currentNotes = []
        self.startNotes = []
        self.stopNotes = []
        
        
        # Find spectrum values above threshold
        idx = 0
        while idx < self.numUsableBins:
            # If the spectrum amplitude is higher than threshold
            if self.transformed[idx] > self.noteDetectionThreshold:
                print("Detected note: idx=",idx)
                # Find corresponding midi note number
                noteNum = self.noteMap[idx]
                
                # Set note to playing in the master note array
                self.masterNoteArray[noteNum].isPlaying = True
                
                # Save note in currently playing list
                self.currentNotes.append(noteNum)
                
                # Debug
#                 print("Playing note:", noteNum, "at idx=", idx)
                
                # We don't have to inspect any more of the transformed array that correspond to this note
                nextNoteNum = noteNum + 1
                if(nextNoteNum < self.numPlayableNotes):
                    # If there is another playable note to start inspection, then
                    # Start looking at its lowest frequency bin
                    idx = self.masterNoteArray[nextNoteNum].lowestNoteIdx
                    
                    # Debug
                    print("skipping to idx=", idx)
                else:
                    # We have finished note inspection, kick out
                    break
            else:
                idx += 1
        
        # Check notes playing to determine if starting or stopping any notes
        for noteNum in self.currentNotes:
            if noteNum not in self.previousNotes:
                self.startNotes.append(noteNum)
        
        for noteNum in self.previousNotes:
            if noteNum not in self.currentNotes:
                self.stopNotes.append(noteNum)
        
        return self.startNotes, self.stopNotes
    
    
    
    
    
    

if __name__ == '__main__':
    import matplotlib.pyplot as plt
    
    fs = 44100.0
    Ts = 1/fs

    t0 = 0
    tf = 0.1

    f1 = 440.0
    f2 = 261.6

    t = np.arange(t0, tf, Ts)

    sig1 = np.sin(2*np.pi*f1*t)
    sig2 = 2*np.sin(2*np.pi*f2*t)

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
    nd = NoteDetector(len(sig3), Ts)

    # Run fft
    transformed = nd.runFFT(sig3)

    # Run note detection
    startNotes, stopNotes = nd.detectNotes()

    
    
    axis[3].set_title('Fourier transform')
    axis[3].plot(nd.farray,transformed)
    axis[3].set_xlabel('Frequency')
    axis[3].set_ylabel('Amplitude')
    
    plt.show()
    
    
    
    # Check that notes are started
    print("First sample")
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
    print("Second sample")
    print("Notes started:")
    for noteNum in startNotes:
        print(noteNum)
    
    # One note should be stopped
    print("Notes stopped:")
    for noteNum in stopNotes:
        print(noteNum)