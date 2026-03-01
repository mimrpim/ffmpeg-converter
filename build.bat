@echo off
setlocal enabledelayedexpansion
:: Zajistíme, že pracovní adresář je tam, kde je tento BAT soubor
cd /d "%~dp0"

:: --- NASTAVENÍ VERZE (Hned na začátku pro všechno) ---
echo ========================================
set /p VERZE="Zadej verzi projektu (napr. 1.1): "
echo ========================================
".venv/Scripts/python.exe" "7zip-install.py"
:: --- ČÁST 1: TVŮJ PŮVODNÍ BUILD.BAT (ZACHOVÁNO 1:1) ---
echo.
echo ========================================
echo 1. SPUSTENE BUILDU (PyInstaller)
echo ========================================

:: Aktivace virtuálního prostředí
call ".venv/Scripts/activate.bat"

:: Instalace requirements
pip install -r requirements.txt

:: Fixní název podle tvého originálu (nemění se)
set BASE_NAME=converter to videostudio pro x9
:: Cílový název složky s verzí
set APP_NAME=%BASE_NAME%-%VERZE%

:: Spuštění PyInstalleru (přesně podle tvého originálu, název zůstává fixní)
pyinstaller --noconfirm --onedir --windowed --icon="icon.ico" --add-data "icon.ico;." --name "%BASE_NAME%" main.py %*

:: Přejmenování vygenerované složky na verzi (pokud už neexistuje)
echo Prejmenovavam slozku na verzi...
if exist "dist\%BASE_NAME%" (
    if exist "dist\%APP_NAME%" rd /s /q "dist\%APP_NAME%"
    ren "dist\%BASE_NAME%" "%APP_NAME%"
)

:: --- ČÁST 2: ARCHIVACE DO VERZOVANÉ SLOŽKY (7za.exe) ---
echo.
echo ========================================
echo 2. DOPLNKOVA ARCHIVACE
echo ========================================

set SEVENZIP_EXE=.7zip\7za.exe
set VERSION_FOLDER=dist\%VERZE%
set SOURCE_DIR=dist\%APP_NAME%
set ZIP_OUTPUT=dist\%VERZE%-win.zip

:: Kontrola, zda existuje 7za.exe
if not exist "%SEVENZIP_EXE%" (
    echo CHYBA: %SEVENZIP_EXE% nenalezen, preskakuji baleni do ZIPu.
    pause
    exit /b
)

:: Vytvoření složky verze (např. dist\1.1)
if not exist "%VERSION_FOLDER%" (
    mkdir "%VERSION_FOLDER%"
)

:: Zabalení obsahu pomocí 7za.exe do formátu ZIP
if exist "%SOURCE_DIR%" (
    echo Balim obsah %SOURCE_DIR% do %ZIP_OUTPUT%...
    "%SEVENZIP_EXE%" a -tzip "%ZIP_OUTPUT%" ".\%SOURCE_DIR%\*"
) else (
    echo CHYBA: Slozka %SOURCE_DIR% nebyla nalezena.
)

echo.
echo ========================================
echo HOTOVO! 
echo Sestaveno v: %SOURCE_DIR%
echo Archivovano v: %ZIP_OUTPUT%
echo ========================================
pause