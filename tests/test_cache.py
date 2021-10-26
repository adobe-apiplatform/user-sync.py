from pathlib import Path
from datetime import datetime, timedelta
from user_sync.cache.base import CacheBase
from user_sync.cache.sign import SignCache
from sign_client.model import DetailedUserInfo, GroupInfo, UserGroupInfo


def test_init_no_store(tmp_path):
    """test CacheBase.init with non-existent store"""
    store_path: Path = tmp_path / 'cache' / 'sign'
    cb = CacheBase()
    cb.init(store_path)
    meta_path = store_path / cb.cache_meta_filename
    assert store_path.exists()
    assert meta_path.exists()
    assert cb.should_refresh

    conn = cb.cache_meta_conn
    cur = conn.cursor()
    cur.execute("SELECT next_refresh FROM cache_meta")
    next_refresh, = cur.fetchone()
    assert type(next_refresh) == datetime

def test_init_expired_cache(tmp_path):
    """test CacheBase.init with expired cache"""
    store_path: Path = tmp_path / 'cache' / 'sign'
    cb = CacheBase()
    cb.init(store_path)
    cb.should_refresh = False
    conn = cb.cache_meta_conn
    cur = conn.cursor()
    cur.execute("DELETE FROM cache_meta")
    expired_ts = datetime.now() - timedelta(seconds=CacheBase.refresh_interval+60)
    cur.execute('INSERT INTO cache_meta VALUES (?)', (expired_ts, ))
    conn.commit()
    cb = CacheBase()
    cb.init(store_path)
    assert cb.should_refresh

def test_init_valid_cache(tmp_path):
    """test CacheBase.init with valid cache"""
    store_path: Path = tmp_path / 'cache' / 'sign'
    cb = CacheBase()
    cb.init(store_path)
    cb.init(store_path)
    assert not cb.should_refresh

def test_sign_db_file(tmp_path):
    """Ensure creation of sign cache file"""
    store_path: Path = tmp_path / 'cache' / 'sign'
    org_name = 'primary'
    SignCache(store_path, org_name)
    assert (store_path / f"{org_name}.db").exists()

def test_sign_should_refresh(tmp_path):
    """If Sign cache is initialized, we should refresh"""
    store_path: Path = tmp_path / 'cache' / 'sign'
    org_name = 'primary'
    cache = SignCache(store_path, org_name)
    assert cache.should_refresh

def test_sign_cache_schema(tmp_path):
    """Ensure Sign cache tables exist"""
    store_path: Path = tmp_path / 'cache' / 'sign'
    org_name = 'primary'
    cache = SignCache(store_path, org_name)
    conn = cache.db_conn
    cur = conn.cursor()
    table_check_query = "SELECT name FROM sqlite_master WHERE type='table' AND name=?"
    for table in ['users', 'groups', 'user_groups']:
        cur.execute(table_check_query, (table,))
        assert cur.fetchone() is not None
    cur.close()

def test_cache_user(tmp_path):
    """Insert a user to cache and retrieve it"""
    store_path: Path = tmp_path / 'cache' / 'sign'
    org_name = 'primary'
    cache = SignCache(store_path, org_name)
    cache.cache_user(DetailedUserInfo(
        accountType='GLOBAL',
        email='user@example.com',
        id='12345abc',
        isAccountAdmin=False,
        status='ACTIVE',
    ))
    assert cache.get_users()[0].email == 'user@example.com'

def test_cache_group(tmp_path):
    """Insert a group to cache and retrieve it"""
    store_path: Path = tmp_path / 'cache' / 'sign'
    org_name = 'primary'
    cache = SignCache(store_path, org_name)
    cache.cache_group(GroupInfo(
        groupId='abc123',
        groupName='Test Group',
        createdDate='right about now',
        isDefaultGroup=False,
    ))
    assert cache.get_groups()[0].groupId == 'abc123'

def test_cache_user_group(tmp_path):
    """Insert a user group to cache and retrieve it"""
    store_path: Path = tmp_path / 'cache' / 'sign'
    org_name = 'primary'
    cache = SignCache(store_path, org_name)
    cache.cache_user_group('12345abc', UserGroupInfo(
        id='abc123',
        isGroupAdmin=False,
        isPrimaryGroup=True,
        status='ACTIVE',
    ))
    assert cache.get_user_groups('12345abc')[0].id == 'abc123'
