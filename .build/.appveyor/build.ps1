if ($env:python.endswith("36-x64")) {
    $pycmd = "${env:python}\python.exe"
    & $pycmd -m venv venv
} else {
    $venvcmd = "${env:python}\Scripts\virtualenv.exe"
    & $venvcmd venv
}
.\venv\Scripts\activate.ps1
pip install external\okta-0.0.3.1-py2.py3-none-any.whl
pip install -e .
pip install -e .[test]
pip install -e .[setup]

if ($env:python.endswith("36-x64")) {
    pip uninstall -y enum34
}

make $env:BUILD_TARGET 2>&1
dir dist
mkdir release

cp dist\user-sync.exe release\
cd release
7z a "user-sync-${env:APPVEYOR_REPO_TAG_NAME}${env:BUILD_EDITION}-win64.zip" user-sync.exe
cd ..
7z a -ttar -r release\examples.tar examples
7z a -tgzip release\examples.tar.gz release\examples.tar
7z a -r release\examples.zip examples\
dir release
