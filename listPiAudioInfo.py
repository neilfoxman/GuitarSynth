# https://people.csail.mit.edu/hubert/pyaudio/docs/

import pyaudio

p = pyaudio.PyAudio()
print("\n~~~~~~~~~~\n")

# print("Getting default input device info as FYI:")
# print(p.get_default_input_device_info())

print("\nNum API count:")
numApis = p.get_host_api_count()
print(numApis)

print("Host API's:")
for idx in range(0, numApis):
	print(p.get_host_api_info_by_index(idx))

print("\nNum Device count:")
numDevices = p.get_device_count()
print(numDevices)

print("Host devices:")
for idx in range(0,numDevices):
	devinfo = p.get_device_info_by_index(idx)
	#print(devinfo)
	print("idx=", idx)
	print("name=", devinfo["name"])
	print("defaultSampleRate=", devinfo['defaultSampleRate'])
	print("maxInputChannels=", devinfo["maxInputChannels"])
	print("maxOutputChannels=", devinfo["maxOutputChannels"])
	print("hostApi=", devinfo["hostApi"])
	print("\n")
	
p.terminate()
