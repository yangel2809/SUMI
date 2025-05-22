@echo off

REM Navega al directorio del script
cd /d "%~dp0"

REM Activa el entorno virtual
call env\Scripts\activate.bat

REM instala las dependencias necesarias
pip install -r requirements.txt

REM Ejecuta el servidor Django en la IP y puerto deseados
python manage.py runserver 0.0.0.0:9000

REM Mantiene la ventana abierta
cmd /k