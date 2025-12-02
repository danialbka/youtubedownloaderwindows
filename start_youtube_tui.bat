@echo off
setlocal enabledelayedexpansion
cd /d "%~dp0"

echo ============================================
echo      YOUTUBE DOWNLOADER TUI
echo ============================================
echo.

:: Check if Python is installed (try both python and python3)
python --version >nul 2>&1
if errorlevel 1 (
    python3 --version >nul 2>&1
    if errorlevel 1 (
        echo [ERROR] Python is not installed or not in PATH
        echo.
        echo Please install Python from https://python.org
        echo Make sure to check "Add Python to PATH" during installation!
        echo.
        pause
        exit /b 1
    ) else (
        set PYTHON=python3
        set PIP=pip3
    )
) else (
    set PYTHON=python
    set PIP=pip
)

echo Using: !PYTHON!
echo.

:: Check and install dependencies
echo Checking and installing dependencies...
echo.

!PIP! show yt-dlp >nul 2>&1
if errorlevel 1 (
    echo Installing yt-dlp ^(video downloader^)...
    !PIP! install yt-dlp
)

!PIP! show rich >nul 2>&1
if errorlevel 1 (
    echo Installing rich ^(terminal UI^)...
    !PIP! install rich
)

echo.
echo All dependencies installed!
echo.
echo ============================================
echo    Starting YouTube Downloader TUI...
echo ============================================
echo.

:: Run the YouTube-only TUI
!PYTHON! youtube_tui.py

echo.
pause
endlocal
