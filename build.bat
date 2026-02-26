@echo off
:: Aktivace virtuálního prostředí
call ".venv/Scripts/activate.bat"

:: Instalace requirements (pokud je spouštíš často, můžeš zakomentovat pro zrychlení)
pip install -r requirements.txt

:: Spuštění hlavního skriptu a předání všech parametrů (souborů) přes %*
pyinstaller --onefile --windowed main.py --onedir --icon=icon.ico

pause