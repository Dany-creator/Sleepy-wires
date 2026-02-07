@echo off
echo ============================================
echo  VISUAL DESIGN EVALUATOR - INICIO RAPIDO
echo ============================================
echo.

REM Verificar si existe el entorno virtual
if not exist "venv\" (
    echo [1/4] Creando entorno virtual...
    python -m venv venv
    echo.
) else (
    echo [1/4] Entorno virtual ya existe
    echo.
)

REM Activar entorno virtual
echo [2/4] Activando entorno virtual...
call venv\Scripts\activate
echo.

REM Verificar si existe .env
if not exist ".env" (
    echo [3/4] Creando archivo .env desde plantilla...
    copy .env.example .env
    echo.
    echo IMPORTANTE: Edita el archivo .env y agrega tu ANTHROPIC_KEY
    echo.
    pause
) else (
    echo [3/4] Archivo .env encontrado
    echo.
)

REM Instalar dependencias
echo [4/4] Instalando dependencias...
pip install -r requirements.txt
echo.

REM Verificar configuracion
echo Verificando configuracion...
python config.py
echo.

REM Preguntar que ejecutar
echo ============================================
echo Como quieres usar el evaluador?
echo ============================================
echo.
echo 1. Interfaz Web (recomendado)
echo 2. Linea de comandos
echo 3. Solo verificar instalacion
echo.
set /p choice="Elige una opcion (1/2/3): "

if "%choice%"=="1" (
    echo.
    echo Iniciando servidor web...
    echo Abre tu navegador en: http://localhost:5000
    echo.
    python app_visual.py
) else if "%choice%"=="2" (
    echo.
    python evaluate_visual.py
) else (
    echo.
    echo Instalacion completada. Ejecuta:
    echo   python app_visual.py     - Para interfaz web
    echo   python evaluate_visual.py - Para linea de comandos
)

pause
