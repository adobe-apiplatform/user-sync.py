RM := rm -rf
python_ldap_requirements := misc/build/python-ldap-requirements.txt
secure_credential_requirements := misc/build/secure-credential-requirements.txt
needs_secure_credential_backend_packages = yes

ifeq ($(OS),Windows_NT)
	output_file_extension = .pex
	needs_secure_credential_backend_packages = no
	rm_path := $(shell python -c "import distutils.spawn; print(distutils.spawn.find_executable('rm'))")
ifeq ($(rm_path),None)
	RM := rmdir /S /Q
endif
	python_arch := $(shell python -c "import platform; print platform.architecture()[0]")
ifeq ($(python_arch),64bit)
	python_ldap_requirements := misc/build/Win64/python-ldap-requirements.txt
endif

else
	OS := $(shell uname)
ifeq ($(OS),Darwin)
	needs_secure_credential_backend_packages = no
endif
endif

ifeq ($(needs_secure_credential_backend_packages), yes)
	secure_credential_requirements := misc/build/linux/secure-credential-requirements.txt
endif

output_dir = dist
output_filename = user-sync

pex:
	pip install --upgrade pip
	pip install pex requests wheel
	pip wheel -w wheelhouse -r misc/build/requirements.txt -r $(python_ldap_requirements) -r $(secure_credential_requirements)
	-$(RM) $(output_dir)
	pex \
		-v -o $(output_dir)/$(output_filename)$(output_file_extension) -m user_sync.app \
		-f wheelhouse \
		--disable-cache \
		--not-zip-safe .
	-$(RM) wheelhouse

test:
	nosetests --no-byte-compile tests
