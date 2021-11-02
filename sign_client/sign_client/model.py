# Copyright (c) 2016-2021 Adobe Inc.  All rights reserved.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
import dataclasses
from dataclasses import dataclass
import json


class JSONEncoder(json.JSONEncoder):
        def default(self, o):
            new_dct = {}
            if dataclasses.is_dataclass(o):
                dct = dataclasses.asdict(o)
            else:
                dct = o
            for k, v in dct.items():
                if v is None:
                    continue
                if isinstance(v, dict):
                    new_dct[k] = self.default(v)
                elif isinstance(v, list):
                    new_dct[k] = [self.default(i) for i in v]
                else:
                    new_dct[k] = v
            return new_dct

@dataclass
class PageInfo:
    nextCursor: str = None

    @classmethod
    def from_dict(cls, dct):
        return cls(**dct)


@dataclass
class UserInfo:
    email: str
    id: str
    isAccountAdmin: bool
    accountId: str = None
    company: str = None
    firstName: str = None
    lastName: str = None

    @classmethod
    def from_dict(cls, dct):
        return cls(**dct)


@dataclass
class UsersInfo:
    page: PageInfo
    userInfoList: list[UserInfo]

    @classmethod
    def from_dict(cls, dct):
        userInfoList = [UserInfo(**u) for u in dct['userInfoList']]
        return cls(page=PageInfo(**dct['page']), userInfoList=userInfoList)


@dataclass
class DetailedUserInfo:
    accountType: str
    email: str
    id: str
    isAccountAdmin: bool
    status: str
    accountId: str = None
    company: str = None
    createdDate: str = None
    firstName: str = None
    initials: str = None
    lastName: str = None
    locale: str = None
    phone: str = None
    primaryGroupId: str = None
    title: str = None

    @classmethod
    def from_dict(cls, dct):
        return cls(**dct)


@dataclass
class GroupInfo:
    groupId: str
    groupName: str
    createdDate: str = None
    isDefaultGroup: bool = None

    @classmethod
    def from_dict(cls, dct):
        return cls(**dct)


@dataclass
class DetailedGroupInfo:
    name: str
    id: str = None
    createdDate: str = None
    isDefaultGroup: bool = False

    @classmethod
    def from_dict(cls, dct):
        return cls(**dct)


@dataclass
class GroupsInfo:
    page: PageInfo
    groupInfoList: list[GroupInfo]

    @classmethod
    def from_dict(cls, dct):
        groupInfoList = [GroupInfo(**u) for u in dct['groupInfoList']]
        return cls(page=PageInfo(**dct['page']), groupInfoList=groupInfoList)


@dataclass
class BooleanSettingsInfo:
    value: bool
    inherited: bool

    @classmethod
    def from_dict(cls, dct):
        return cls(**dct)


@dataclass
class SettingsInfo:
    libaryDocumentCreationVisible: BooleanSettingsInfo = None
    sendRestrictedToWorkflows: BooleanSettingsInfo = None
    userCanSend: BooleanSettingsInfo = None

    @classmethod
    def from_dict(cls, dct):
        new_dct = {k: BooleanSettingsInfo.from_dict(v) for k, v in dct.items()}
        return cls(**new_dct)


@dataclass
class UserGroupInfo:
    id: str
    isGroupAdmin: bool
    isPrimaryGroup: bool
    status: str
    createdDate: str = None
    name: str = None
    settings: SettingsInfo = None

    @classmethod
    def from_dict(cls, dct):
        new_dct = {}
        for k, v in dct.items():
            if k == 'settings':
                new_dct[k] = SettingsInfo.from_dict(v)
            else:
                new_dct[k] = v
        return cls(**new_dct)


@dataclass
class UserGroupsInfo:
    groupInfoList: list[UserGroupInfo]

    @classmethod
    def from_dict(cls, dct):
        return cls([UserGroupInfo.from_dict(v) for v in dct['groupInfoList']])
