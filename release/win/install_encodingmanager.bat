@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

:: Show language options
echo Select the language of the file you want to install:
echo.
echo 1. German (DE)
echo 2. English (EN)
echo 3. Italian (IT)
echo 4. Spanish (ES)
echo 5. French (FR)
echo 6. Czech (CS)
echo 7. Polish (PL)
echo 8. Dutch (NL)
echo.

set /p langChoice=Please enter the number (1–8):

:: Set language code based on selection
set "langCode="
if "%langChoice%"=="1" set langCode=DE
if "%langChoice%"=="2" set langCode=EN
if "%langChoice%"=="3" set langCode=IT
if "%langChoice%"=="4" set langCode=ES
if "%langChoice%"=="5" set langCode=FR
if "%langChoice%"=="6" set langCode=CS
if "%langChoice%"=="7" set langCode=PL
if "%langChoice%"=="8" set langCode=NL

if "%langCode%"=="" (
    echo Invalid selection. Script will exit.
    pause
    exit /b
)

:: Define source file
set "SOURCE_FILE=Encodingmanager_%langCode%.py"

:: Check if the source file exists
if not exist "%SOURCE_FILE%" (
    echo Error: The file "%SOURCE_FILE%" was not found in the current folder.
    pause
    exit /b
)

:: Define target directory
set "TARGET_DIR=C:\Users\%USERNAME%\AppData\Roaming\Blackmagic Design\DaVinci Resolve\Support\Fusion\Scripts\Edit"

:: Create target directory if it doesn't exist
if not exist "%TARGET_DIR%" (
    mkdir "%TARGET_DIR%"
)

:: Copy the file
copy /Y "%SOURCE_FILE%" "%TARGET_DIR%"

echo.
echo ✓ File "%SOURCE_FILE%" has been successfully copied to:
echo   %TARGET_DIR%
pause
