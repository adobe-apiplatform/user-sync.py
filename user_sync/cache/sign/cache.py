from ..base import CacheBase
from sign_client.model import DetailedUserInfo, GroupInfo, UserGroupInfo
from pathlib import Path

class SignCache(CacheBase):
    def __init__(self, store_path: Path, org_name: str) -> None:
        self.init(store_path)
        db_path = store_path / f"{org_name}.db"
        self.db_conn = self.get_db_conn(db_path)
        super().__init__()
