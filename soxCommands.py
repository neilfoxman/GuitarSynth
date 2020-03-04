""" SoX commands """
OVERDRIVE_CMD = "overdrive 20 20" # gain, color
CHORUS_CMD = "chorus 0.7 0.9 55 0.4 0.25 2 -t" # gain-in gain-out delay decay speed depth sin/triangle
DELAY_CMD = "delay 0.5" # seconds
FLANGER_CMD = "flanger"
PHASE_CMD = "phaser 0.89 0.85 1 0.24 2 -t" # gain-in gain-out delay decay speed sin/triangle
PITCH_CMD = "pitch 10" # cents
REVERB_CMD = "reverb -w" # wet (vs dry)
TEMOLO_CMD = "tremolo 20 40" # speed depth
