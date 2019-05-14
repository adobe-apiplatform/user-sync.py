output_dir = dist
output_filename = user-sync
prebuilt_dir = external

ifeq ($(OS),Windows_NT)
	output_file_extension = .pex
	rm_path := $(shell python -c "import distutils.spawn; print(distutils.spawn.find_executable('rm'))")
    ifeq ($(rm_path),None)
        RM := rmdir /S /Q
    else
	    RM := $(rm_path) -rf
    endif
else
    output_file_extension = ""
    RM := rm -rf
endif

pex:
	python -m pip install --upgrade pip
	python -m pip install --upgrade 'wheel<0.30.0' requests pex==1.5.3
	python .build/pre_build.py
	-$(RM) $(output_dir)
	pex -v -o $(output_dir)/$(output_filename)$(output_file_extension) -m user_sync.app \
		-f $(prebuilt_dir) \
		--disable-cache \
		--not-zip-safe .

standalone:
	python -m pip install --upgrade pip
	python -m pip install --upgrade pyinstaller
	python -m pip install --upgrade setuptools
	python .build/pre_build.py
	pyinstaller --clean --noconfirm user-sync.spec

test:
	nosetests --no-byte-compile tests
