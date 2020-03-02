import mido
import time

print(mido.get_output_names())
#port = mido.open_output('Midi Through:Midi Through Port-0 14:0')

with mido.open_output('Midi Through:Midi Through Port-0 14:0') as outport:
    msg = mido.Message('note_on', note=60)
    outport.send(msg)
    time.sleep(1)
    msg = mido.Message('note_off', note=60)
    outport.send(msg)
    

outport.reset()
outport.close()