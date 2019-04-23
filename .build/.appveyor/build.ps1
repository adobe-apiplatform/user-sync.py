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

if ($env:BUILD_TARGET -eq "pex") {
    cp dist\user-sync.pex release\
    cd release\
    Get-Command python
    $pyver = $( python -V 2>&1 ) -replace "Python ", "py" -replace "\.", ""
    echo "pyver: ${pyver}"
    7z a -ttar "user-sync-${env:APPVEYOR_REPO_TAG_NAME}-win64-${pyver}.tar" user-sync.pex
    7z a -tgzip "user-sync-${env:APPVEYOR_REPO_TAG_NAME}-win64-${pyver}.tar.gz" "user-sync-${env:APPVEYOR_REPO_TAG_NAME}-win64-${pyver}.tar"
    7z a "user-sync-${env:APPVEYOR_REPO_TAG_NAME}-win64-${pyver}.zip" user-sync.pex
    cd ..
    7z a -ttar -r release\examples.tar examples
    7z a -tgzip release\examples.tar.gz release\examples.tar
    7z a -r release\examples.zip examples\
} else {
    cp dist\user-sync.exe release\
    cd release
    mv user-sync.exe "user-sync-${env:APPVEYOR_REPO_TAG_NAME}-win64.exe"
    cd ..
}
dir release
