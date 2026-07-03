@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

title PyQalculate v0.1.0
cd /d "%~dp0"

:: ---- fixed paths (no dependency on activate.bat) ----
set PY=.venv\Scripts\python.exe
set PIP=%PY% -m pip

echo.
echo ========================================
echo   PyQalculate v0.1.0 - Python Calculator
echo ========================================
echo.

:: Check system Python exists
echo [1/2] Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo Python is not installed!
    echo Please install Python 3.10 or later.
    echo Download: https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('python --version 2^>^&1') do echo Found %%i

:: Check virtual environment
echo [2/2] Checking virtual environment...
set VENV_VALID=0
if exist "%PY%" (
    %PY% -c "" >nul 2>&1
    if not errorlevel 1 set VENV_VALID=1
)

if %VENV_VALID%==0 (
    if exist ".venv" (
        echo Virtual environment is incomplete. Recreating...
        rmdir /s /q ".venv"
    )
    echo Creating virtual environment...
    python -m venv .venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment.
        echo Please ensure Python is installed and accessible.
        pause
        exit /b 1
    )

    echo Installing dependencies...
    %PIP% install -e . --require-virtualenv
    if errorlevel 1 (
        echo ERROR: Failed to install dependencies.
        echo Retrying without --require-virtualenv...
        %PIP% install -e .
    )

    echo Installing optional dependencies...
    %PIP% install matplotlib sympy gmpy2 --require-virtualenv

    echo Virtual environment created successfully.
    @REM Touch a marker to avoid full check on next runs
    %PY% -c ""
) else (
    echo Virtual environment found.

    echo   Checking dependencies...
    %PIP% install -e . --require-virtualenv
    if errorlevel 1 (
        echo   Retrying without --require-virtualenv...
        %PIP% install -e .
    )

    :: Sanity-check key imports (detect orphaned metadata / missing module files)
    echo   Verifying imports...
    %PY% -c "import sympy,gmpy2,mpmath,pint,convertdate,matplotlib,numpy,scipy,requests,PIL,dateutil,pyreadline3" >nul 2>&1
    if errorlevel 1 (
        echo   [!] Broken packages detected. Force-reinstalling...
        %PIP% install --force-reinstall sympy gmpy2 mpmath pint convertdate matplotlib numpy scipy requests Pillow python-dateutil pyreadline3
    )
)

echo.
echo Press any key to continue...
pause >nul
cls

:MENU
echo ========================================
echo           Main Menu
echo ========================================
echo   [1] CLI Mode     - Command line calculator
echo   [2] GUI Mode     - Graphical calculator
echo   [3] Run Tests    - Run all test suites
echo   [4] Run Demo     - Run all demos
echo   [0] Exit
echo ========================================
echo.

set /p choice=Select [0-4]: 

if "%choice%"=="1" goto CLI
if "%choice%"=="2" goto GUI
if "%choice%"=="3" goto TEST
if "%choice%"=="4" goto DEMO
if "%choice%"=="0" goto EXIT

echo Invalid choice!
echo.
goto RETURN

:CLI
echo.
echo Starting CLI Mode...
echo Type 'quit' to exit the calculator.
echo.
%PY% scripts\cli.py
echo.
goto RETURN

:GUI
echo.
echo Starting GUI Mode...
%PY% scripts\gui.py
echo.
goto RETURN

:TEST
echo.
echo Installing test dependencies...
%PIP% install -e ".[dev]" -q
%PY% scripts\test_runner.py
echo.
goto RETURN

:DEMO
echo.
%PY% scripts\demo.py
echo.
goto RETURN

:RETURN
echo.
pause
cls
goto MENU

:EXIT
echo.
echo Goodbye!
echo.
pause
endlocal
exit /b 0
