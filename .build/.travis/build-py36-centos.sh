#!/usr/bin/env bash
python3 -m venv venv
source venv/bin/activate
python -m pip install --upgrade pip
pip install external/okta-0.0.3.1-py2.py3-none-any.whl
pip install -e .
pip install -e .[test]
pip install -e .[setup]
pip uninstall -y enum34
make $BUILD_TARGET
pwd
.build/.travis/release.sh
python setup.py test
