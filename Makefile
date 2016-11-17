
ifeq ($(OS),Windows_NT)
	RM = rmdir /S /Q
	python_ldap_requirements = misc/build/Win64/python-ldap-requirements.txt
	output_file_extension = .pex
else
	RM = rm -rf
	python_ldap_requirements = misc/build/python-ldap-requirements.txt
endif

output_dir = dist
output_filename = aed_sync

pex:
	pip install --upgrade pip
	pip install pex requests wheel
	pip wheel -w wheelhouse -r misc/build/requirements.txt -r $(python_ldap_requirements)
	$(RM) $(output_dir)
	pex \
		-v -o $(output_dir)/$(output_filename)$(output_file_extension) -m aedash.sync.app \
		-f wheelhouse \
		--disable-cache \
		--not-zip-safe .
	$(RM) wheelhouse

