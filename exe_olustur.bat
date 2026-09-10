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
    echo   4^) Kurulum bitince bu pencereyi kapatip yeniden ac
    echo   5^) Bu dosyaya tekrar cift tikla
    echo.
    pause
    exit /b 1
)

echo Kullanilan komut: %PYCMD%  ^(surumu asagida^)
%PYCMD% --version

echo.
echo Bagimliliklar ve PyInstaller kuruluyor ^(ilk seferde birkac dakika surebilir^)...
%PYCMD% -m pip install --upgrade pip
%PYCMD% -m pip install -r requirements.txt
%PYCMD% -m pip install pyinstaller
if errorlevel 1 (
    echo.
    echo HATA: kurulum basarisiz oldu. Yukaridaki pip hata mesajini
    echo bana gonder, birlikte bakalim.
    pause
    exit /b 1
)

echo.
echo Onceki derlemeden acik kalmis olabilecek exe kapatiliyor
echo ^(calismiyorsa bu adim zaten bir sey yapmaz^)...
taskkill /f /im PixelDrop.exe >nul 2>&1
taskkill /f /im SuIcmeHatirlatici.exe >nul 2>&1
timeout /t 1 /nobreak >nul

echo.
echo Konsolsuz .exe olusturuluyor ^(klasor modu - bu birkac dakika surebilir^)...
%PYCMD% -m PyInstaller --onedir --noconsole --noupx --name PixelDrop --add-data "pixeldrop\i18n;pixeldrop\i18n" main.py
if errorlevel 1 (
    echo.
    echo HATA: PyInstaller derlemesi basarisiz oldu. Yukaridaki hatayi
    echo bana gonder, birlikte bakalim.
    pause
    exit /b 1
)

echo.
echo ==============================================
echo  Bitti: dist\PixelDrop\PixelDrop.exe
echo ==============================================
echo.
echo Simdi calistiriliyor - hicbir konsol/cmd penceresi ACILMAMALI,
echo sadece sag alttaki tepsi simgesi ve masaustu widget'i gorunmeli.
start "" "dist\PixelDrop\PixelDrop.exe"

echo.
echo Not: exe'yi kalici olarak kullanacaksan, ayarlardan (ya da tepsi
echo menusunden) "Windows baslangicinda calistir" secenegini bir KEZ
echo kapatip tekrar ac - baslangic kaydi boylece .py yerine bu exe'yi
echo gosterir.
echo.
echo Onemli: exe tek dosya yerine artik dist\PixelDrop\ klasorunun
echo icinde (PixelDrop.exe + yaninda gerekli dosyalar). GitHub'a ya da
echo baskasina gonderirken TUM "PixelDrop" klasorunu ZIP'leyip oyle
echo paylas - tek basina exe'yi paylasmak, PyInstaller ile derlenmis
echo tum exe'lerde cok yaygin gorulen bir sorun yuzunden Windows
echo Defender / Chrome / Google tarafindan yanlislikla "zararli
echo yazilim" olarak isaretlenebiliyor (bilinen bir yanlis pozitif -
echo klasor modu bu riski onemli olcude azaltir).
pause
