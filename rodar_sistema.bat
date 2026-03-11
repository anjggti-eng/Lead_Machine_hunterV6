@echo off
title Debug Lead Machine
color 0b

echo.
echo ==========================================
echo    DEBUGGING LEAD MACHINE STARTUP
echo ==========================================
echo.

:: Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERRO] Python nao foi encontrado no seu Windows PATH.
    echo Por favor, instale o Python e marque a opcao "Add Python to PATH".
    pause
    exit /b
)

echo [OK] Python detectado.
cd /d "%~dp0"

:: Check if venv exists
if not exist venv (
    echo [1/4] Criando ambiente virtual...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo [ERRO] Falha ao criar o venv. Verifique permissoes.
        pause
        exit /b
    )
)

echo [2/4] Verificando dependencias...
if not exist venv\Scripts\pip.exe (
    echo [ERRO] Venv nao encontrado ou corrompido.
    pause
    exit /b
)

echo [3/4] Instalando dependencias (por favor, aguarde)...
venv\Scripts\pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [AVISO] Teve problemas ao instalar dependencias, tentando seguir...
)

echo [4/4] Iniciando Banco e Servidor...
venv\Scripts\python init_db.py
start http://127.0.0.1:5050
venv\Scripts\python app.py

if %errorlevel% neq 0 (
    echo.
    echo [ERRO CRITICO] O servidor Flask falhou ao iniciar.
    pause
)

pause
