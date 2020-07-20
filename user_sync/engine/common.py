GROUP_NAME_DELIMITER = '::'
PRIMARY_TARGET_NAME = None


class AdobeGroup:
    index_map = {}

    def __init__(self, group_name, umapi_name, index=True):
        """
        :type group_name: str
        :type umapi_name: str
        """
        self.group_name = group_name
        self.umapi_name = umapi_name
        if index:
            AdobeGroup.index_map[(group_name, umapi_name)] = self

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(frozenset(self.__dict__))

    def __str__(self):
        return str(self.__dict__)

    def get_qualified_name(self):
        prefix = ""
        if self.umapi_name is not None and self.umapi_name != PRIMARY_TARGET_NAME:
            prefix = self.umapi_name + GROUP_NAME_DELIMITER
        return prefix + self.group_name

    def get_umapi_name(self):
        return self.umapi_name

    def get_group_name(self):
        return self.group_name

    @staticmethod
    def _parse(qualified_name):
        """
        :type qualified_name: str
        :rtype: str, str
        """
        parts = qualified_name.split(GROUP_NAME_DELIMITER)
        group_name = parts.pop()
        umapi_name = GROUP_NAME_DELIMITER.join(parts)
        if len(umapi_name) == 0:
            umapi_name = PRIMARY_TARGET_NAME
        return group_name, umapi_name

    @classmethod
    def lookup(cls, qualified_name):
        return cls.index_map.get(cls._parse(qualified_name))

    @classmethod
    def create(cls, qualified_name, index=True):
        group_name, umapi_name = cls._parse(qualified_name)
        existing = cls.index_map.get((group_name, umapi_name))
        if existing:
            return existing
        elif len(group_name) > 0:
            return cls(group_name, umapi_name, index)
        else:
            return None

    @classmethod
    def iter_groups(cls):
        return cls.index_map.items()
