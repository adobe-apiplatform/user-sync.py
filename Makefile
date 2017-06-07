USE_WHEEL := no
RM := rm -rf

ifeq ($(OS),Windows_NT)
	output_file_extension = .pex
	rm_path := $(shell python -c "import distutils.spawn; print(distutils.spawn.find_executable('rm'))")
ifeq ($(rm_path),None)
	RM := rmdir /S /Q
endif
	python_arch := $(shell python -c "import platform; print platform.architecture()[0]")
ifeq ($(python_arch),64bit)
	python_ldap_requirements := misc/build/Win64/python-ldap-requirements.txt
	USE_WHEEL := yes
endif
endif

output_dir = dist
output_filename = user-sync

pex:
	pip install --upgrade pip
	pip install pex requests wheel
	-$(RM) $(output_dir)
ifeq ($(USE_WHEEL),yes)
	pip wheel -w wheelhouse -r $(python_ldap_requirements)
	pex \
		-v -o $(output_dir)/$(output_filename)$(output_file_extension) -m user_sync.app \
		-f wheelhouse \
		--disable-cache \
		--not-zip-safe .
	-$(RM) wheelhouse
else
	pex \
		-v -o $(output_dir)/$(output_filename)$(output_file_extension) -m user_sync.app \
		--disable-cache \
		--not-zip-safe .
endif

test:
	nosetests --no-byte-compile tests
