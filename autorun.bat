@echo off

REM Check if Python is installed and in the PATH
python --version >nul 2>&1
if errorlevel 1 (
    echo Python no esta instalado o no se encuentra su variable en PATH.
    echo Presione cualquier tecla para salir...
    pause >nul
    exit /b
)

REM Check if pip is installed and in the PATH
pip --version >nul 2>&1
if errorlevel 1 (
    echo pip no esta instalado o no esta en el PATH. Usando "python -m pip" en su lugar...
    set PIP_CMD=python -m pip
) else (
    set PIP_CMD=pip
)


REM Define the environment name
set ENV_NAME=env

REM Check if the environment exists
if not exist "%ENV_NAME%" (
    echo No existe un entorno virtual "env". Creando...
    python -m venv env

    echo Iniciando entorno e instalando dependencias...

    call env\Scripts\activate.bat
    %PIP_CMD% install -r requirements.txt
)

REM Activate the environment, restart NGINX and run the script
echo Activnado entorno virtual...
call env\Scripts\activate.bat
REM echo Comprobando y cerrando instancias actuales de NGINX...
REM taskkill /f /IM nginx.exe
echo Iciando NGINX...
start nginx
REM for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /C:"IPv4 Address"') do echo Servicio iniciado en%%a:9000
call python server.py
pause >nul
exit /b
