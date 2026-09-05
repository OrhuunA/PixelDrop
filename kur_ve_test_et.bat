@echo off
setlocal enabledelayedexpansion
cd /d "%~dp0"

echo Python araniyor...
set PYCMD=

where python >nul 2>&1
if not errorlevel 1 (
    python --version >nul 2>&1
    if not errorlevel 1 set PYCMD=python
)

if "%PYCMD%"=="" (
    where py >nul 2>&1
    if not errorlevel 1 (
        py -3 --version >nul 2>&1
        if not errorlevel 1 set PYCMD=py -3
    )
)

if "%PYCMD%"=="" (
    echo.
    echo HATA: Bilgisayarinda calisan bir Python kurulumu bulunamadi.
    echo.
    echo Cozum:
    echo   1^) https://www.python.org/downloads/ adresine git
    echo   2^) Indirilen kurulumu calistir
    echo   3^) Kurulum ekraninin EN ALTINDAKI "Add python.exe to PATH"
    echo      kutucugunu MUTLAKA isaretle
    echo   4^) Kurulum bitince bu bilgisayari/oturumu yeniden baslat
    echo      ^(ya da en azindan bu pencereyi kapatip yeniden ac^)
    echo   5^) Bu dosyaya tekrar cift tikla
    echo.
    pause
    exit /b 1
)

echo Kullanilan komut: %PYCMD%  ^(surumu asagida^)
%PYCMD% --version

echo.
echo Bagimliliklar kuruluyor ^(ilk seferde birkac dakika surebilir^)...
%PYCMD% -m pip install --upgrade pip
%PYCMD% -m pip install -r requirements.txt
if errorlevel 1 (
    echo.
    echo HATA: bagimliliklar kurulamadi. Yukaridaki pip hata mesajini
    echo bana gonder, birlikte bakalim.
    pause
    exit /b 1
)

echo.
echo Test bildirimi gonderiliyor...
%PYCMD% main.py --test-notify

echo.
echo Tepsi ^(tray^) uygulamasi baslatiliyor. Sag alttaki mavi damla simgesini kontrol et.
echo Kapatmak icin: simgeye sag tikla - Cikis, ya da bu pencereyi kapat.
%PYCMD% main.py
pause
