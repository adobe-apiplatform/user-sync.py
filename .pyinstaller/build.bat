@echo off

REM pip uninstall enum34
REM pip install pywin32
REM pip install pyinstaller
REM Batch file:

pyinstaller.exe ^
    --clean ^
    --noconfirm ^
    --onefile  ^
    --hidden-import=win32timezone ^
    --additional-hooks-dir=. ^
    --specpath=dist ^
    ..\user_sync\app.py

move dist\app.exe dist\user-sync.exe

