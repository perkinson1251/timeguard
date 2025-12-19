@echo off
echo ==========================================
echo Building TimeGuard.exe
echo ==========================================
echo.

REM Check if PyInstaller is installed
python -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo PyInstaller not found. Installing...
    pip install pyinstaller
)

echo Cleaning old build files...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist TimeGuard.exe del /q TimeGuard.exe

echo.
echo Building executable...
pyinstaller TimeGuard.spec

echo.
if exist "dist\TimeGuard.exe" (
    echo ==========================================
    echo Build SUCCESS!
    echo ==========================================
    echo Executable location: dist\TimeGuard.exe
    echo File size:
    dir "dist\TimeGuard.exe" | find "TimeGuard.exe"
) else (
    echo ==========================================
    echo Build FAILED!
    echo ==========================================
    echo Check the output above for errors.
)

echo.
pause
