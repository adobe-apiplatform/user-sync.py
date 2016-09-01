import os
import psutil
from contextlib import contextmanager


@contextmanager
def create_lock(path):
    lock = ProcessLock(path)
    yield lock
    if lock.is_locked():
        lock.unlock()


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
        pid = os.getpid()
        with open(self.path, 'w') as f:
            f.write(str(pid))

    def unlock(self):
        os.remove(self.path)
