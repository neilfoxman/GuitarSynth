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

I had issues installing matplotlib using pip for debugging, but installing it through apt-get worked
```
sudo apt-get install python-matplotlib
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
Can test pyaudio using test scripts on https://people.csail.mit.edu/hubert/pyaudio/docs/  
Assuming script is saved in file called `pyaudiotest.py`, go to test script location and run 
```
python pyaudiotest.py /usr/share/sounds/alsa/Front_Center.wav
```
Pyaudio will spit out a bunch of debug messages at line with pyaudio.PyAudio()
but that is ok according to https://stackoverflow.com/questions/7088672/pyaudio-working-but-spits-out-error-messages-each-time

### Choosing devices
If no USB audio device is connected, the default devices are:
```
Host devices:
('name=', u'bcm2835 ALSA: IEC958/HDMI (hw:0,1)')
('defaultSampleRate=', 44100.0)
('maxInputChannels=', 0L)
('maxOutputChannels=', 8L)
('hostApi=', 0L)


('name=', u'bcm2835 ALSA: IEC958/HDMI1 (hw:0,2)')
('defaultSampleRate=', 44100.0)
('maxInputChannels=', 0L)
('maxOutputChannels=', 8L)
('hostApi=', 0L)


('name=', u'dmix')
('defaultSampleRate=', 48000.0)
('maxInputChannels=', 0L)
('maxOutputChannels=', 2L)
('hostApi=', 0L)
```

With no input devices.  
When the USB audio device is connected, you get these additional devices:
```
('name=', u'USB Audio Device: - (hw:1,0)')
('defaultSampleRate=', 44100.0)
('maxInputChannels=', 1L)
('maxOutputChannels=', 2L)
('hostApi=', 0L)


('name=', u'output')
('defaultSampleRate=', 44100.0)
('maxInputChannels=', 1L)
('maxOutputChannels=', 2L)
('hostApi=', 0L)


('name=', u'input')
('defaultSampleRate=', 44100.0)
('maxInputChannels=', 1L)
('maxOutputChannels=', 2L)
('hostApi=', 0L)

('name=', u'default')
('defaultSampleRate=', 44100.0)
('maxInputChannels=', 128L)
('maxOutputChannels=', 128L)
('hostApi=', 0L)
```
