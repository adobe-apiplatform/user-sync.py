# Copyright (c) 2016-2017 Adobe Systems Incorporated.  All rights reserved.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import os
import psutil


class ProcessLock(object):
    def __init__(self, path):
        self.path = path

    def is_locked(self):
        # process is not locked if lock file does not exist
        if not os.path.exists(self.path):
            return False

        # if lock file exists, get pid
        with open(self.path, 'r') as f:
            lock_pid = f.read().strip()

        if not lock_pid:
            return False

        lock_pid = int(lock_pid)
        
        if psutil.pid_exists(lock_pid):
            return True
        else:
            return False

    def set_lock(self):
        success = False
        if not self.is_locked():
            pid = os.getpid()
            with open(self.path, 'w') as f:
                f.write(str(pid))
            success = True
        return success 

    def unlock(self):
        os.remove(self.path)
