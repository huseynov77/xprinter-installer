@echo off
setlocal enabledelayedexpansion

:: ═══ CloPos XPrinter Build & Release Script ═══
:: Bu script PyInstaller ile EXE build edir ve GitHub-a release olaraq yukleyir.

:: Versiyani printer_installer faylindan oxu
for /f "tokens=2 delims==" %%A in ('findstr /R "^VERSION" printer_installer_v*.py 2^>nul ^| sort /R ^| head -1') do (
    set "RAW=%%A"
)
:: Manual olaraq versiyani daxil et
set /p "VER=Versiya daxil edin (meselen 8.1): "
if "%VER%"=="" (
    echo Versiya daxil edilmedi!
    exit /b 1
)

set "PY_FILE=printer_installer_v%VER%.py"
set "SPEC_FILE=CloPos XPrinter Install v%VER%.spec"
set "EXE_NAME=CloPos XPrinter Install v%VER%"
set "DIST_EXE=dist\%EXE_NAME%.exe"
set "UPLOAD_NAME=CloPos.XPrinter.Install.v%VER%.exe"
set "TAG=v%VER%"

echo.
echo ══════════════════════════════════════════
echo   CloPos XPrinter Build ^& Release v%VER%
echo ══════════════════════════════════════════
echo.

:: 1) Python faylinin movcudlugunu yoxla
if not exist "%PY_FILE%" (
    echo [X] %PY_FILE% tapilmadi!
    exit /b 1
)
echo [OK] %PY_FILE% tapildi

:: 2) PyInstaller ile build
echo.
echo [*] PyInstaller ile build edilir...
if exist "%SPEC_FILE%" (
    pyinstaller "%SPEC_FILE%" --noconfirm --clean
) else (
    pyinstaller --onefile --noconsole --name "%EXE_NAME%" ^
        --add-data "XPrinter Driver Setup V7.77.exe;." ^
        --add-data "CloPos_XPrinter_UserGuide.pdf;." ^
        --icon clopos_xprinter.ico ^
        --collect-all certifi ^
        "%PY_FILE%"
)

if not exist "%DIST_EXE%" (
    echo [X] Build ugursuz! %DIST_EXE% tapilmadi.
    exit /b 1
)
echo [OK] Build tamamlandi: %DIST_EXE%

:: 3) EXE-ni GitHub upload ucun kopyala (noqteli ad)
copy "%DIST_EXE%" "%UPLOAD_NAME%" >nul
echo [OK] %UPLOAD_NAME% hazirdir

:: 4) Git commit & push
echo.
echo [*] Git commit ve push...
git add "%PY_FILE%" "%SPEC_FILE%" 2>nul
git commit -m "v%VER% release" 2>nul
git push origin main 2>nul

:: 5) GitHub Release yarat
echo.
echo [*] GitHub Release yaradilir: %TAG%
C:\gh\bin\gh.exe release delete %TAG% --yes 2>nul
C:\gh\bin\gh.exe release create %TAG% "%UPLOAD_NAME%" ^
    --title "CloPos XPrinter Installer v%VER%" ^
    --notes "CloPos XPrinter Auto-Installer v%VER% release" ^
    --latest

if errorlevel 1 (
    echo [X] GitHub Release yaradilmadi!
    exit /b 1
)

echo.
echo ══════════════════════════════════════════
echo   [OK] v%VER% GitHub-a yuklendi!
echo   https://github.com/huseynov77/xprinter-installer/releases/tag/%TAG%
echo ══════════════════════════════════════════

:: Temizle
del "%UPLOAD_NAME%" 2>nul

endlocal
