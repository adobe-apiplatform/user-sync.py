RM := rm -rf

ifeq ($(OS),Windows_NT)
	output_file_extension = .pex
	rm_path := $(shell python -c "import distutils.spawn; print(distutils.spawn.find_executable('rm'))")
	ifeq ($(rm_path),None)
		RM := rmdir /S /Q
	endif
endif

output_dir = dist
output_filename = user-sync-test

pex:
	pip install --upgrade pip
	pip install pex requests wheel
	-$(RM) $(output_dir)
	pex \
		-v -o $(output_dir)/$(output_filename)$(output_file_extension) -m user_sync_test.app \
		--disable-cache \
		--not-zip-safe .
