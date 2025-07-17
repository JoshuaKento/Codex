@echo off
REM Setup Python environment using pyenv-win
set PYTHON_VERSION=3.11.4

pyenv install -s %PYTHON_VERSION%
pyenv local %PYTHON_VERSION%

pyenv exec python -m venv venv
call venv\Scripts\activate

pip install -r requirements.txt
