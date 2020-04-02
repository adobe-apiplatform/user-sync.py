
# -----------------------------------------------------------------------------
# Copyright (c) 2013-2018, PyInstaller Development Team.
#
# Distributed under the terms of the GNU General Public License with exception
# for distributing bootloader.
#
# The full license is in the file COPYING.txt, distributed with this software.
# -----------------------------------------------------------------------------

# Temporary implementation until this PR is merged:
# https://github.com/pyinstaller/pyinstaller/pull/3948/files

# See also https://github.com/jaraco/keyring/issues/324

from PyInstaller.utils.hooks import collect_submodules, copy_metadata

hiddenimports = collect_submodules('keyrings.cryptfile.cryptfile')

# keyring uses entrypoints to read keyring.backends from metadata file entry_points.txt.
datas = copy_metadata('keyrings.cryptfile')