@echo off
:: Aktivace virtuálního prostředí
call ".venv/Scripts/activate.bat"

:: Instalace requirements (pokud je spouštíš často, můžeš zakomentovat pro zrychlení)
pip install -r requirements.txt

:: Spuštění hlavního skriptu a předání všech parametrů (souborů) přes %*
pyinstaller --noconfirm --onedir --windowed --icon="icon.ico" --add-data "icon.ico;." --name "converter to videostudio pro x9" main.py

pause