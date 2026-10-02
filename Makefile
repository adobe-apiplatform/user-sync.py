output_dir = dist
output_filename = user-sync
prebuilt_dir = external

ifeq ($(OS),Windows_NT)
	rm_path := $(shell python -c "import shutil; print(shutil.which('rm'))")
    ifeq ($(rm_path),None)
        RM := rmdir /S /Q
    else
	    RM := $(rm_path) -rf
    endif
else
    RM := rm -rf
endif

standalone:
	python -m pip install --upgrade pip
	python -m pip install --upgrade pyinstaller
	python -m pip install --upgrade setuptools
	-$(RM) $(output_dir)
	python .build/pre_build.py
	pyinstaller --clean --noconfirm user-sync.spec

test:
	nosetests --no-byte-compile tests
