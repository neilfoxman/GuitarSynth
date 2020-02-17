# GuitarSynth

## Configuration
### Dependencies
First double check all updated/upgraded
```
sudo apt-get update
sudo apt-get upgrade
```

Need to install python dev tools PortAudio (C and C++ dependency) and PyAudio
https://people.csail.mit.edu/hubert/pyaudio/

```
sudo apt-get install python-all-dev
sudo apt-get install portaudio19-dev
sudo apt-get install python-pyaudio python3-pyaudio
```
### Testing
Use the command below to check the audio devices/cards available.
USB device should be card 1
```
aplay -l
```
Test speakers using raspberry pi stock wav files  
You may need to select audio device used by right clicking speaker in upper right
corner and selecting correct device
```
aplay /usr/share/sounds/alsa/Front_Center.wav
```
Can test pyaudio using test script at the bottom of https://people.csail.mit.edu/hubert/pyaudio/  
Assuming script is saved in file called `pyaudiotest.py`, go to test script location and run 
```
python pyaudiotest.py /usr/share/sounds/alsa/Front_Center.wav
```
