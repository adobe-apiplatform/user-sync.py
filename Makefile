pex:
	pip install --upgrade pip
	pip install pex requests wheel
	pip wheel -w wheelhouse -r requirements.txt
	pex \
		-v -o dist/aedc -m aedash_connector.app \
		-f wheelhouse \
		--disable-cache \
		--not-zip-safe .
	rm -rf wheelhouse
