from pathlib import Path
from datetime import datetime, timedelta
from user_sync.cache.base import CacheBase


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

def test_version_number(tmp_path):
    """Make sure version number is stored properly"""
    store_path: Path = tmp_path / 'cache' / 'sign'
    cb = CacheBase()
    cb.init(store_path)
    assert cb.get_version() == CacheBase.VERSION
