import os
import pytest
import psutil
import user_sync.lockfile as lock

@pytest.fixture
def get_lock_filepath():
    return os.path.join(os.getcwd(), 'lockfile_test')

def test_set_lock():

    # use to set lock file
    # assert lock file exists
    # assert that PID in lockfile matches this process PID
    pass

def test_is_locked(get_lock_filepath):
    test_path = get_lock_filepath

    plock = lock.ProcessLock("./randompath/lockfile")
    assert plock.is_locked() is False

    plock.path = test_path
    with open(test_path, 'w') as f:
        f.write("")
    assert plock.is_locked() is False

    with open(test_path, 'w') as f:
        f.write("dfsdf")
    pytest.raises(ValueError, plock.is_locked)

    with open(test_path, 'w') as f:
        f.write("1234")
    assert plock.is_locked() is False

    with open(test_path, 'w') as f:
        f.write(str(os.getpid()))
    assert plock.is_locked() is True

    # any other cases that make sense ///

    pass

def test_unlock():

    # run setlock
    # verify file exists
    # run unlock
    # assert is_locked = false
    pass
