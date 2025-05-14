@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

rem Sprachoptionen anzeigen
echo Wähle die Sprache der Datei, die du installieren möchtest:
echo.
echo 1. Deutsch (DE)
echo 2. Englisch (EN)
echo 3. Italienisch (IT)
echo 4. Spanisch (ES)
echo 5. Französisch (FR)
echo 6. Tschechisch (CS)
echo 7. Polnisch (PL)
echo 8. Niederländisch (NL)
echo.

set /p langChoice=Bitte gib die Zahl ein (1–8):

rem Sprachkürzel entsprechend der Auswahl setzen
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
    echo Ungültige Auswahl. Skript wird beendet.
    pause
    exit /b
)

rem Quelldatei festlegen
set "SOURCE_FILE=Encodingmanager_%langCode%.py"

rem Prüfen, ob die Quelldatei existiert
if not exist "%SOURCE_FILE%" (
    echo Fehler: Die Datei "%SOURCE_FILE%" wurde im aktuellen Ordner nicht gefunden.
    pause
    exit /b
)

rem Zielverzeichnis definieren
set "TARGET_DIR=C:\Users\%username%\AppData\Roaming\Blackmagic Design\DaVinci Resolve\Support\Scripts\Deliver"

rem Zielverzeichnis erstellen, falls es nicht existiert
if not exist "%TARGET_DIR%" (
    mkdir "%TARGET_DIR%"
)

rem Datei kopieren
copy /Y "%SOURCE_FILE%" "%TARGET_DIR%"

echo.
echo ✓ Datei "%SOURCE_FILE%" wurde erfolgreich nach:
echo   %TARGET_DIR%
echo kopiert.
pause
