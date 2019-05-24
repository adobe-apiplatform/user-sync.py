import os
import pytest
import user_sync.lockfile as lock


@pytest.fixture
def lock_filepath():
    path = os.path.join(os.getcwd(), 'lockfile_test')
    remove_lockfile(path)
    return path


def test_set_lock(lock_filepath):
    plock1 = lock.ProcessLock(lock_filepath)
    assert plock1.set_lock() is True
    remove_lockfile(lock_filepath)


def test_is_locked(lock_filepath):
    plock = lock.ProcessLock(lock_filepath)
    assert plock.is_locked() is False

    plock.path = lock_filepath
    with open(lock_filepath, 'w') as f:
        f.write("")
    assert plock.is_locked() is False

    with open(lock_filepath, 'w') as f:
        f.write("dfsdf")
    pytest.raises(ValueError, plock.is_locked)
    remove_lockfile(lock_filepath)


def test_unlock(lock_filepath):
    plock2 = lock.ProcessLock(lock_filepath)
    assert plock2.set_lock()
    assert plock2.is_locked()

    plock2.unlock()
    assert not plock2.is_locked()
    assert not os.path.exists(lock_filepath)
    remove_lockfile(lock_filepath)

def remove_lockfile(path):
    try:
        os.remove(path)
    except:
        pass
