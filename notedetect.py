# Neil Foxman and Alexander King, CSE 237A #
# Reference Material:
# https://pythontic.com/visualization/signals/fouriertransform_fft
import numpy as np
import math

MIDI_DICT = {0: 'C', 1: 'C#', 2: 'D', 3: 'D#', 4: 'E',
             5: 'F', 6: 'F#', 7: 'G', 8: 'G#', 9: 'A',
             10: 'A#', 11: 'B'}

def noteToLetter(note):
    return MIDI_DICT[note%12] + str(note//12 - 1)

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
        noteArray = np.array(noteList)
        return noteArray

    def generateMasterNoteArray(self, noteMap):
        masterNoteList = []

        # Find maximum note number used (last entry in noteMap)
        maxNote = noteMap[self.numUsableBins - 1]
        
        # Create an array of note objects up to and including that number
        for noteNumber in range(maxNote + 1):
            masterNoteList.append(Note(noteNumber))
        masterNoteArray = np.array(masterNoteList)
        
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
            
            # Start looking at the next lower index
            inspectedIdx -= 1
        
        # Diagnostics - The bins generated by fft are spaced out in a linear scale while
        # acoustic notes are spaced out on a logarithmic scale (see conversion functions).
        # This means that the lower midi notes may not have corresponding
        # frequency bins after fft().  This section detects the lowest sequential frequency.

        # Count down from highest frequency
        for idx in reversed(range(self.numUsableBins)):
            if(idx-1 < 0):
                print("All midi notes can be played!")
            
            elif((noteMap[idx-1] != noteMap[idx]) and
                 (noteMap[idx-1] != noteMap[idx] - 1)):
                print("Lowest sequential playable note is ", noteMap[idx])
                break
        
        return masterNoteArray
        
    def runFFT(self, signal):
        # Transform array into frequency domain
        transformed_all = np.fft.rfft(signal)
        
        # Exclude redundant frequencies due to discrete transform
        transformed = abs(transformed_all[self.usableBins])
        
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
            # If the spectrum amplitude is higher than threshold (indicating a note is being played)
            if self.transformed[idx] > self.noteDetectionThreshold:
                # Find the corresponding midi note number
                noteNum = self.noteMap[idx]
                
                # Set note to playing in the master note array
                note = self.masterNoteArray[noteNum]
                note.isPlaying = True
                
                # Save note in currently playing list
                self.currentNotes.append(noteNum)

                # Skip-Ahead Section
                # We don't have to inspect any more of the transformed array at indices that also
                # correspond to this note
                # Look for the starting index of the next note (saved on the master note array)
                nextNoteFound = False
                nextNoteNum = noteNum + 1
                while not nextNoteFound:
                    # If the next note is within the playable notes
                    if(nextNoteNum < self.numPlayableNotes):
                        
                        # If the next note can be associated with a spot on the frequency array
                        # Get the lowest index associated with that note
                        tempIdx = self.masterNoteArray[nextNoteNum].lowestNoteIdx
                        
                        # If that index found is reasonable
                        if(tempIdx >= 0):
                            # Then jump ahead and continue scanning the transformation array at that index
                            nextNoteFound = True
                            idx = tempIdx
                        else:
                            # The next note has not been properly mapped (number of samples is too low)
                            # Look at the next playable note
                            nextNoteNum += 1
                        
                    else:
                        # The next note pitch is too high.  Stop scanning the transformation array
                        idx = self.numUsableBins # highest index, will halt outer loop
                        nextNoteFound = True
                        break

            else: # If this value is below the threshold
                # Look at the next frequency bin
                idx += 1
        
        # Check notes playing to determine if starting or stopping any notes
        for noteNum in self.currentNotes:
            if noteNum not in self.previousNotes:
                self.startNotes.append(noteNum)
        
        for noteNum in self.previousNotes:
            if noteNum not in self.currentNotes:
                self.stopNotes.append(noteNum)
        
        return self.startNotes, self.stopNotes
