# Codex

## Noise Player

This repository includes a simple noise generator with a small GUI for
real-time playback. The application requires `sounddevice` and `tkinter`.

### Running

```bash
./setup.sh
python brown_noise_player.py
```
The `setup.sh` script creates a Python virtual environment in `venv` and installs the dependencies from `requirements.txt`.

### Windows (pyenv-win)

Install [pyenv-win](https://github.com/pyenv-win/pyenv-win) and then run:

```powershell
.\setup_pyenv.bat
.\venv\Scripts\python.exe brown_noise_player.py
```
The batch file uses `pyenv` to ensure a suitable Python version is available, then creates the `venv` directory and installs the packages.

Move the volume slider to adjust the output level. Choose the wave type from
the drop-down list to switch between brown noise, white noise and a sine wave.
Use the **Start** and **Stop** buttons to control playback. Playback continues
even when the window is not in the foreground. Brown noise generation uses a
stable filter so it won't stall during long sessions. Select the output device
from the new menu if your system has multiple audio outputs.

## Pomodoro Timer

This repository also includes a lightweight Pomodoro timer widget. Click the
circular ring to choose a duration from 0–60 minutes. Selected segments of the
ring glow in **red** and the timer begins counting down immediately. The current
time is shown at the top.

### Running

```bash
python pomodoro_timer.py
```

The circular ring is a smooth outline representing sixty minutes. Clicking
anywhere along the ring selects that many minutes and starts the countdown.
The timer remains synchronized with the system clock, ensuring that each
second ticks in real time. A schedule panel on the right side lists every
15‑minute slot from 00:00 to 24:00 so you can jot down plans for the day.
The current time is highlighted in this list.
Two new buttons let you **Import** a text file into the schedule panel and
**Export** its contents for later use.
