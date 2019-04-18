#!/usr/bin/env bash

# sudo apt install binutils (? Ubuntu)

# pip install pyinstaller
# pip install -e .
# pip uninstall enum34

pyinstaller \
    --clean \
    --noconfirm \
    --onefile  \
    --additional-hooks-dir=. \
    --specpath=dist \
    ../user_sync/app.py

rm dist/app.spec
rm -rf build
mv dist/app dist/user-sync