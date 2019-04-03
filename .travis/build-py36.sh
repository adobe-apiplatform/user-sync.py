#!/usr/bin/env bash
pip install external/okta-0.0.3.1-py2.py3-none-any.whl
pip install -e .
pip install -e .[test]
pip install -e .[setup]
pip uninstall -y enum34
make
