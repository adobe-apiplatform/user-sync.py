
import aedash.sync.error

def open_file(name, mode, buffering = -1):
    '''
    :type name: str
    :type mode: str
    :type buffering: int
    '''
    try:
        return open(name, mode, buffering)
    except IOError as e:
        raise aedash.sync.error.AssertionException(str(e))