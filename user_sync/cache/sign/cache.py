from ..base import CacheBase
from .schema import sign_groups as sign_groups_schema
from .schema import sign_users as sign_users_schema
from .schema import sign_user_groups as sign_user_groups_schema
from sign_client.model import DetailedUserInfo, GroupInfo, UserGroupInfo, JSONEncoder
from pathlib import Path
import json
import sqlite3
from collections import defaultdict

class SignCache(CacheBase):
    def __init__(self, store_path: Path, org_name: str) -> None:
        sqlite3.register_adapter(DetailedUserInfo, adapt_user)
        sqlite3.register_converter("detailed_user_info", convert_user)
        sqlite3.register_adapter(GroupInfo, adapt_group)
        sqlite3.register_converter("group_info", convert_group)
        sqlite3.register_adapter(UserGroupInfo, adapt_user_group)
        sqlite3.register_converter("user_group_info", convert_user_group)
        self.init(store_path)
        db_path = store_path / f"{org_name}.db"
        if not db_path.exists():
            self.should_refresh = True
            self.db_conn = self.get_db_conn(db_path)
            for s in [sign_users_schema, sign_groups_schema, sign_user_groups_schema]:
                self.db_conn.execute(s)
            self.db_conn.commit()
        else:
            self.db_conn = self.get_db_conn(db_path)
        super().__init__()
    
    def clear_all(self):
        self.db_conn.execute("delete from users")
        self.db_conn.execute("delete from groups")
        self.db_conn.execute("delete from user_groups")
        self.db_conn.commit()

    def cache_user(self, user: DetailedUserInfo):
        self.db_conn.execute("insert into users(id, user) values (?,?)", (user.id, user))
        self.db_conn.commit()

    def update_user(self, user: DetailedUserInfo):
        self.db_conn.execute("update users set user = ? where id = ?", (user, user.id))
        self.db_conn.commit()
    
    def get_users(self) -> list[DetailedUserInfo]:
        cur = self.db_conn.cursor()
        cur.execute("select user from users")
        return [r[0] for r in cur.fetchall()]

    def get_user(self, user_id) -> DetailedUserInfo:
        cur = self.db_conn.cursor()
        cur.execute("select user from users where id = ?", (user_id, ))
        return cur.fetchone()[0]

    def cache_group(self, group: GroupInfo):
        self.db_conn.execute("insert into groups(id, group_info) values (?,?)", (group.groupId, group))
        self.db_conn.commit()

    def delete_group(self, group: GroupInfo):
        self.db_conn.execute("delete from groups where id = ?", (group.groupId, ))
        self.db_conn.commit()
    
    def get_groups(self) -> list[GroupInfo]:
        cur = self.db_conn.cursor()
        cur.execute("select group_info from groups")
        return [r[0] for r in cur.fetchall()]

    def cache_user_group(self, user_id: str, user_group: UserGroupInfo):
        self.db_conn.execute("insert into user_groups(user_id, user_group) values (?,?)", (user_id, user_group))
        self.db_conn.commit()
    
    def get_user_groups(self) -> list[tuple[str, list[UserGroupInfo]]]:
        groups_by_user = defaultdict(list)
        cur = self.db_conn.cursor()
        cur.execute("select user_id, user_group from user_groups")
        for user_id, user_group in cur.fetchall():
            groups_by_user[user_id].append(user_group)
        return list(groups_by_user.items())

    def update_user_groups(self, user_id: str, user_groups: list[UserGroupInfo]):
        self.db_conn.execute("delete from user_groups where user_id = ?", (user_id, ))
        self.db_conn.commit()
        for user_group in user_groups:
            self.cache_user_group(user_id, user_group)

def adapt_user(user: DetailedUserInfo) -> str:
    return json.dumps(user.__dict__, cls=JSONEncoder).encode('ascii')

def convert_user(s: str) -> DetailedUserInfo:
    return DetailedUserInfo.from_dict(json.loads(s))

def adapt_group(group: GroupInfo) -> str:
    return json.dumps(group.__dict__, cls=JSONEncoder).encode('ascii')

def convert_group(s: str) -> GroupInfo:
    return GroupInfo.from_dict(json.loads(s))

def adapt_user_group(user_group: UserGroupInfo) -> str:
    return json.dumps(user_group.__dict__, cls=JSONEncoder).encode('ascii')

def convert_user_group(s: str) -> UserGroupInfo:
    return UserGroupInfo.from_dict(json.loads(s))
