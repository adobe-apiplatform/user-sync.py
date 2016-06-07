pex:
	virtualenv pex-build-cache
	pex-build-cache/bin/pip install --upgrade pip
	pex-build-cache/bin/pip install pex requests wheel
	pex-build-cache/bin/pip wheel -w pex-build-cache/wheelhouse -r requirements.txt
	pex-build-cache/bin/pex \
		-v -o dist/aedc -m aedash_connector.app:main \
		-f pex-build-cache/wheelhouse \
		--disable-cache \
		--not-zip-safe .
	rm -rf pex-build-cache
