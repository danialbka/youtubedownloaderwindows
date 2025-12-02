@echo off
setlocal
cd /d "%~dp0"

:: Build a standalone Windows exe for the YouTube TUI using PyInstaller.
:: If Python is missing, this script will download and install it automatically.
:: Requirements: Windows with internet access.

echo ============================================
echo   Building youtube_tui.exe (PyInstaller)
echo ============================================
echo.

set PY=
set PIP=

:: Detect python
for %%P in (python python3) do (
    %%P --version >nul 2>&1
    if not errorlevel 1 (
        set PY=%%P
    )
)

:: If not found, download and install Python (per-user, adds to PATH)
if "%PY%"=="" (
    echo Python not found. Downloading Python 3.12.3...
    set "PY_VER=3.12.3"
    set "PY_URL=https://www.python.org/ftp/python/%PY_VER%/python-%PY_VER%-amd64.exe"
    set "PY_TMP=%TEMP%\\python-installer.exe"

    powershell -Command "Invoke-WebRequest -Uri '%PY_URL%' -OutFile '%PY_TMP%'" >nul 2>&1
    if errorlevel 1 (
        echo [ERROR] Failed to download Python installer.
        pause
        exit /b 1
    )

    echo Installing Python (per-user, adding to PATH)...
    "%PY_TMP%" /quiet InstallAllUsers=0 PrependPath=1 Include_test=0
    if errorlevel 1 (
        echo [ERROR] Python install failed.
        pause
        exit /b 1
    )

    del /f /q "%PY_TMP%" >nul 2>&1

    :: Refresh PATH for this session by locating the newly installed python
    for %%P in ("%LocalAppData%\\Programs\\Python\\Python312\\python.exe" "%ProgramFiles%\\Python312\\python.exe") do (
        if exist %%P (
            set PY=%%P
        )
    )

    if "%PY%"=="" (
        :: Fallback to PATH search in case installer updated PATH mid-session
        for %%P in (python python3) do (
            %%P --version >nul 2>&1
            if not errorlevel 1 (
                set PY=%%P
            )
        )
    )
)

if "%PY%"=="" (
    echo [ERROR] Could not locate Python after installation.
    pause
    exit /b 1
)

echo Using: %PY%
echo.
set "PIP=%PY% -m pip"

:: Ensure dependencies (PyInstaller plus runtime libs)
echo Installing build dependencies...
%PIP% install --upgrade pyinstaller yt-dlp rich >nul
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies.
    pause
    exit /b 1
)

:: Build
echo.
echo Running PyInstaller...
%PY% -m PyInstaller --onefile --name youtube_tui ^
    --add-data "functions;functions" ^
    youtube_tui.py

if errorlevel 1 (
    echo [ERROR] Build failed.
    pause
    exit /b 1
)

echo.
echo Build complete!
echo Your exe is at: %cd%\dist\youtube_tui.exe
echo.
pause
endlocal
