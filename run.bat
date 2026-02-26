@echo off
:: Aktivace virtuálního prostředí
call ".venv/Scripts/activate.bat"

:: Instalace requirements (pokud je spouštíš často, můžeš zakomentovat pro zrychlení)
python -m pip install --upgrade pip
pip install -r requirements.txt

:: Spuštění hlavního skriptu a předání všech parametrů (souborů) přes %*
python "./main.py" %*

pause