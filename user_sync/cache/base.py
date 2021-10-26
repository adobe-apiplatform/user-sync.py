import os
from pathlib import Path
import sqlite3
from datetime import datetime
from .schema import cache_meta as cache_meta_schema

class CacheBase:
    should_refresh: bool = False
    cache_meta_filename: str = 'cache-meta.db'
    REFRESH_INTERVAL: int = 86400

    def init(self, store_path: Path):
        meta_path = store_path / self.cache_meta_filename
        if not meta_path.exists():
            self.should_refresh = True
            os.makedirs(store_path, exist_ok=True)
            con = sqlite3.connect(meta_path, detect_types=sqlite3.PARSE_DECLTYPES)
            cur = con.cursor()
            cur.execute(cache_meta_schema)
            cur.execute('INSERT INTO cache_meta VALUES (?)', (datetime.now(), ))
            con.commit()
            cur.close()



