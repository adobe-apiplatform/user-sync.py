sign_users = """
create table if not exists users (
    id text not null unique,
    needs_refresh int default 0,
    user detailed_user_info
);
"""

sign_groups = """
create table if not exists groups (
    id text not null unique,
    group_info group_info
);
"""

sign_user_groups = """
create table if not exists user_groups (
    user_id text not null,
    user_group user_group_info
);
"""
