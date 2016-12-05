RM := rm -rf
python_ldap_requirements := misc/build/python-ldap-requirements.txt

ifeq ($(OS),Windows_NT)
	output_file_extension = .pex
	rm_path := $(shell python -c "import distutils.spawn; print(distutils.spawn.find_executable('rm'))")
ifeq ($(rm_path),None)
	RM := rmdir /S /Q
endif
	python_arch := $(shell python -c "import platform; print platform.architecture()[0]")
ifeq ($(python_arch),64bit)
	python_ldap_requirements := misc/build/Win64/python-ldap-requirements.txt
endif
endif

output_dir = dist
output_filename = aed_sync

pex:
	pip install --upgrade pip
	pip install pex requests wheel
	pip wheel -w wheelhouse -r misc/build/requirements.txt -r $(python_ldap_requirements)
	-$(RM) $(output_dir)
	pex \
		-v -o $(output_dir)/$(output_filename)$(output_file_extension) -m aedash.sync.app \
		-f wheelhouse \
		--disable-cache \
		--not-zip-safe .
	-$(RM) wheelhouse

test:
	nosetests --no-byte-compile tests
