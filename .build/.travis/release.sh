#!/usr/bin/env bash
cd dist
tar czf "user-sync-${TRAVIS_TAG}${BUILD_EDITION}-${IMG}.tar.gz" user-sync
cd ..
mkdir -p release
mv dist/* release/
ls -al release/
