import os
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

        try:
            # signal 0 checks if process exists & we have permission to send signals (we assume that we should)
            os.kill(lock_pid, 0)
        # OSError returned if process doesn't exist (or we don't have permission to signal it)
        except OSError:
            return False
        else:
            return True

    def set_lock(self):
        pid = os.getpid()
        with open(self.path, 'w') as f:
            f.write(str(pid))

    def unlock(self):
        os.remove(self.path)
