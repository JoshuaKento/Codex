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

```cmd
setup_pyenv.bat
python brown_noise_player.py
```
The batch file uses `pyenv` to ensure a suitable Python version is available, creates the `venv` directory and installs the packages.

Move the volume slider to adjust the output level. Choose the wave type from
the drop-down list to switch between brown noise, white noise and a sine wave.
Use the **Start** and **Stop** buttons to control playback. Playback continues
even when the window is not in the foreground. Brown noise generation uses a
stable filter so it won't stall during long sessions.
