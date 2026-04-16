@echo off
REM Negative Language Installer for Windows

echo 🚀 Installing Negative Language...

REM Check Python version
python --version > nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set pyversion=%%i
echo ✅ Python %pyversion% detected

REM Install package
echo 📦 Installing Negative Language...
pip install -e .

REM Run tests (optional)
if "%1"=="--test" (
    echo 🧪 Running tests...
    pytest tests/ -v
)

echo ✅ Negative Language installed successfully!
echo.
echo Try it:
echo   negative --help
echo   negative run examples/security.neg