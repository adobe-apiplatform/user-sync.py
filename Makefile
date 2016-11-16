pex:
	pip install --upgrade pip
	pip install pex requests wheel
	pip wheel -w wheelhouse -r misc/build/requirements.txt
	pex \
		-v -o dist/aed_sync -m aedash.sync.app \
		-f wheelhouse \
		--disable-cache \
		--not-zip-safe .
	rm -rf wheelhouse

