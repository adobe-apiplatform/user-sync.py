@echo off

REM pip install .\external\okta-0.0.3.1-py2.py3-none-any.whl
REM pip install .\external\pyldap-2.4.45-cp36-cp36m-win_amd64.whl
REM pip install pywin32
REM pip install pyinstaller
REM pip install -e .
REM pip uninstall enum34

pyinstaller.exe ^
    --clean ^
    --noconfirm ^
    --onefile  ^
    --hidden-import=win32timezone ^
    --additional-hooks-dir=. ^
    --specpath=dist ^
    ..\user_sync\app.py

rm dist\app.spec
rmdir /s /q build
move dist\app.exe dist\user-sync.exe

