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
	pip install --upgrade pip
	pip install --upgrade 'wheel<0.30.0' requests pex
	-$(RM) $(output_dir)
	pex -v -o $(output_dir)/$(output_filename)$(output_file_extension) -m user_sync.app \
		-f $(prebuilt_dir) \
		--disable-cache \
		--not-zip-safe .

test:
	nosetests --no-byte-compile tests
