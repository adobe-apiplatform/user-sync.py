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
from dataclasses import dataclass


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
    accountId: str
    company: str
    firstName: str
    lastName: str

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
    createdDate: str
    isDefaultGroup: bool

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
