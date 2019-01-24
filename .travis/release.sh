#!/usr/bin/env bash
PY_VER=$(2>&1 python -V | sed -e 's/Python /py/g' | sed -e 's/\.//g')
echo ${PY_VER}
cd dist
tar czf "user-sync-${TRAVIS_TAG}-${IMG}-${PY_VER}.tar.gz" user-sync
ls -al
cd ..
mkdir -p release
mv dist/*.tar.gz release/
ls -al release/
