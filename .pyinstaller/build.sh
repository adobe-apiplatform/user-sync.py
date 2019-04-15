#!/usr/bin/env bash



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