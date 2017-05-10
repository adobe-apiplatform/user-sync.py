RM := rm -rf

ifeq ($(OS),Windows_NT)
	output_file_extension = .pex
	rm_path := $(shell python -c "import distutils.spawn; print(distutils.spawn.find_executable('rm'))")
ifeq ($(rm_path),None)
	RM := rmdir /S /Q
endif
	python_arch := $(shell python -c "import platform; print platform.architecture()[0]")
endif

output_dir = dist
output_filename = config-test

pex:
	pip install --upgrade pip
	pip install pex requests wheel
	pip wheel -w wheelhouse -r requirements.txt
	-$(RM) $(output_dir)
	pex \
		-v -o $(output_dir)/$(output_filename)$(output_file_extension) -m config_test.app \
		-f wheelhouse \
		--disable-cache \
		--not-zip-safe .
	-$(RM) wheelhouse

test:
	nosetests --no-byte-compile tests
