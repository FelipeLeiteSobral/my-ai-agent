@echo off
echo 🚀 START AGENT - Iniciando todos os servicos...
echo.

REM Verificar se Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python nao encontrado! Instale o Python primeiro.
    pause
    exit /b 1
)

REM Verificar se as dependências estão instaladas
echo 📦 Verificando dependencias...
pip install -r requirements.txt >nul 2>&1

REM Iniciar o agente
echo.
echo 🚀 Iniciando o agente...
python start_agent.py

pause

