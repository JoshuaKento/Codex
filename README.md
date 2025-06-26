# Codex

## Noise Player

This repository includes a simple noise generator with a small GUI for
real-time playback. The application requires `sounddevice` and `tkinter`.

### Running

```bash
pip install sounddevice numpy
python brown_noise_player.py
```

Move the volume slider to adjust the output level. Choose the wave type from
the drop-down list to switch between brown noise, white noise and a sine wave.
Use the **Start** and **Stop** buttons to control playback. Playback continues
even when the window is not in the foreground. Brown noise generation uses a
stable filter so it won't stall during long sessions. Select the output device
from the new menu if your system has multiple audio outputs.
