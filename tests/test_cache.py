from pathlib import Path
import sqlite3
from datetime import date, datetime
from user_sync.cache.base import CacheBase


def test_init(tmpdir):
    store_path: Path = tmpdir / 'cache' / 'sign'
    cb = CacheBase()
    cb.init(store_path)
    meta_path = store_path / cb.cache_meta_filename
    assert store_path.exists()
    assert meta_path.exists()
    assert cb.should_refresh

    con = sqlite3.connect(meta_path, detect_types=sqlite3.PARSE_DECLTYPES)
    cur = con.cursor()
    cur.execute("SELECT last_refresh FROM cache_meta")
    last_refresh, = cur.fetchone()
    assert type(last_refresh) == datetime
