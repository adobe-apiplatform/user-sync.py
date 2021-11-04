from pathlib import Path
from datetime import datetime, timedelta
from user_sync.cache.base import CacheBase
from user_sync.cache.sign import SignCache
from sign_client.model import DetailedUserInfo, GroupInfo, UserGroupInfo, SettingsInfo


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
    cur.execute('INSERT INTO cache_meta VALUES (?, ?)', (expired_ts, 1))
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
        settings=SettingsInfo()
    ))
    user_id, user_groups = cache.get_user_groups()[0]
    assert user_groups[0].id == 'abc123'
    assert user_id == '12345abc'

def test_user_update(tmp_path):
    """Test a user update"""
    store_path: Path = tmp_path / 'cache' / 'sign'
    org_name = 'primary'
    cache = SignCache(store_path, org_name)
    user = DetailedUserInfo(
        accountType='GLOBAL',
        email='user@example.com',
        id='12345abc',
        isAccountAdmin=False,
        status='ACTIVE',
    )
    cache.cache_user(user)
    user.isAccountAdmin = True
    cache.update_user(user)
    assert cache.get_users()[0].isAccountAdmin

def test_group_delete(tmp_path):
    """Test a group deletion"""
    store_path: Path = tmp_path / 'cache' / 'sign'
    org_name = 'primary'
    cache = SignCache(store_path, org_name)
    group = GroupInfo(
        groupId='abc123',
        groupName='Test Group',
        createdDate='right about now',
        isDefaultGroup=False,
    )
    cache.cache_group(group)
    assert cache.get_groups()[0].groupId == 'abc123'
    cache.delete_group(group)
    assert cache.get_groups() == []

def test_user_groups_update(tmp_path):
    """Test user groups update"""
    store_path: Path = tmp_path / 'cache' / 'sign'
    org_name = 'primary'
    cache = SignCache(store_path, org_name)
    user_id = '12345abc'
    user_group1 = UserGroupInfo(
        id='abc123',
        isGroupAdmin=False,
        isPrimaryGroup=True,
        status='ACTIVE',
        settings=SettingsInfo()
    )
    cache.cache_user_group(user_id, user_group1)
    user_id, user_groups = cache.get_user_groups()[0]
    assert user_groups[0].id == 'abc123'
    assert user_id == '12345abc'
    user_group2 = UserGroupInfo(
        id='xyz987',
        isGroupAdmin=False,
        isPrimaryGroup=True,
        status='ACTIVE',
        settings=SettingsInfo()
    )
    cache.update_user_groups(user_id, [user_group1, user_group2])
    user_id, user_groups = cache.get_user_groups()[0]
    assert user_id == '12345abc'
    assert len(user_groups) == 2

def test_version_number(tmp_path):
    """Make sure version number is stored properly"""
    store_path: Path = tmp_path / 'cache' / 'sign'
    cb = CacheBase()
    cb.init(store_path)
    assert cb.get_version() == CacheBase.VERSION

def test_version_number_child(tmp_path):
    """Make sure version number is stored properly in child class"""
    store_path: Path = tmp_path / 'cache' / 'sign'
    cache = SignCache(store_path, 'primary')
    assert cache.get_version() == SignCache.VERSION

def test_update_version(tmp_path):
    """test version update"""
    store_path: Path = tmp_path / 'cache' / 'sign'
    cb = CacheBase()
    cb.init(store_path)
    cb.VERSION = 10
    cb.update_version()
    assert cb.get_version() == 10
