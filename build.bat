@echo off
echo =====================================
echo    MINDFUN BUILD SCRIPT
echo =====================================
echo.
echo 1. Bien dich ma nguon bang PyInstaller...
call venv\Scripts\pyinstaller.exe mindfun.spec --noconfirm --clean

echo.
echo 2. Dong goi ban cai dat bang Inno Setup...
set ISCC="C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
if not exist %ISCC% set ISCC="C:\Program Files\Inno Setup 6\ISCC.exe"
if not exist %ISCC% set ISCC="C:\Users\tienr\AppData\Local\Programs\Antigravity IDE\resources\app\node_modules\innosetup\bin\ISCC.exe"

if exist %ISCC% (
    %ISCC% installer\setup.iss
    echo.
    echo HOAN THANH! File cai dat nam trong thu muc: installer\Output\MindfunSetup.exe
) else (
    echo.
    echo Khong tim thay Inno Setup Compiler (ISCC.exe).
    echo Vui long mo file installer\setup.iss bang Inno Setup va an Compile.
)
pause
