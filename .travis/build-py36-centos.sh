#!/usr/bin/env bash
virtualenv venv -p /usr/bin/python3.6
source venv/bin/activate
pip install external/okta-0.0.3.1-py2.py3-none-any.whl
pip install -e .
pip uninstall -y enum34
make
pwd
.travis/release.sh
