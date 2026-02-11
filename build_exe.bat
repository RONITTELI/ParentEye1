@echo off
REM ParentEye - Build Executable Script
REM This script configures and builds the ParentEye_Client.exe

color 0a
cls

echo.
echo ========================================
echo    ParentEye Client - Building EXE
echo ========================================
echo.

REM Check if PyInstaller is installed
pyinstaller --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: PyInstaller not found!
    echo.
    echo Installing PyInstaller...
    python -m pip install pyinstaller
    if errorlevel 1 (
        echo FAILED: Could not install PyInstaller
        echo Install manually: python -m pip install pyinstaller
        pause
        exit /b 1
    )
)

echo [1/3] Configuring client...
python config_client.py

echo.
echo [2/3] Building executable...
echo.

REM Build the exe
pyinstaller ParentEye_Client.spec --clean

if errorlevel 1 (
    color c0
    echo.
    echo ========================================
    echo ERROR: Build Failed!
    echo ========================================
    pause
    exit /b 1
)

cls
color 0a

echo.
echo ========================================
echo    BUILD SUCCESSFUL!
echo ========================================
echo.
echo Output: dist\ParentEye_Client.exe
echo.
echo Next Steps:
echo   1. Copy dist\ParentEye_Client.exe to target PCs
echo   2. Also copy .env file for configuration
echo   3. Run as Administrator on child PC
echo.
echo Files ready for distribution:
echo   - dist\ParentEye_Client.exe
echo   - .env (client configuration)
echo.

pause
