from pathlib import Path
import sqlite3
from datetime import datetime, timedelta
from .schema import cache_meta as cache_meta_schema

class CacheBase:
    should_refresh: bool = False
    cache_meta_filename: str = 'cache-meta.db'
    refresh_interval: int = 86400

    def init(self, store_path: Path):
        self.meta_path = store_path / self.cache_meta_filename
        if not self.meta_path.exists():
            self.should_refresh = True
            store_path.mkdir(parents=True, exist_ok=True)
            self.cache_meta_conn = self.get_db_conn(self.meta_path)
            self.cache_meta_conn.execute(cache_meta_schema)
            self.cache_meta_conn.commit()
            self.update_next_refresh()
        else:
            self.cache_meta_conn = self.get_db_conn(self.meta_path)
            cur = self.cache_meta_conn.cursor()
            cur.execute("SELECT next_refresh FROM cache_meta")
            next_refresh, = cur.fetchone()
            self.should_refresh = next_refresh < datetime.now()
            cur.close()
    
    def __del__(self):
        self.cache_meta_conn.close()
    
    def update_next_refresh(self):
        self.cache_meta_conn = self.get_db_conn(self.meta_path)
        self.cache_meta_conn.execute(cache_meta_schema)
        self.cache_meta_conn.execute("DELETE FROM cache_meta")
        self.cache_meta_conn.execute('INSERT INTO cache_meta VALUES (?)', (datetime.now()+timedelta(seconds=self.refresh_interval), ))
        self.cache_meta_conn.commit()
    
    @staticmethod
    def get_db_conn(db_path: Path) -> sqlite3.Connection:
        return sqlite3.connect(db_path, detect_types=sqlite3.PARSE_DECLTYPES)
