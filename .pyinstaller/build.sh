#!/usr/bin/env bash

#REM pip uninstall enum34
#REM pip install pywin32
#REM pip install pyinstaller

pyinstaller \
    --clean \
    --noconfirm \
    --onefile  \
    --additional-hooks-dir=. \
    --specpath=dist \
    ../user_sync/app.py

#mv dist\app.exe dist\user-sync.exe

  #  --hidden-import=win32timezone \