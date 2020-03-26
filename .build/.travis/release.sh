#!/usr/bin/env bash
PY_VER=$(2>&1 python -V | sed -e 's/Python /py/g' | sed -e 's/\.//g')
echo ${PY_VER}
cd dist
mv user-sync "user-sync-${TRAVIS_TAG}-${IMG}"
cd ..
mkdir -p release
mv dist/* release/
ls -al release/
