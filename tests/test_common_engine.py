from user_sync.engine.common import AdobeGroup
import pytest

class TestAdobeGroup():

    # def test_get_qualified_name(self):
    #     assert self.group_name

    def test_parse(self):
        result = AdobeGroup._parse('qualified_name')
        assert result == ('qualified_name', None)

    def test_create(self):
        group = AdobeGroup.create('group_name')

        assert isinstance(group, AdobeGroup)
        assert group.get_group_name() == 'group_name'