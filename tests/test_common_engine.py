from user_sync.engine.common import AdobeGroup

class TestAdobeGroup():

    def test_get_qualified_name(self):
        #standard test
        self.umapi_name = None
        self.group_name = 'group_name'
        result = AdobeGroup.get_qualified_name(self)
        assert result == ('group_name')

        #umapi_name variation test
        GROUP_NAME_DELIMITER = '::'
        PRIMARY_TARGET_NAME ='not_umapi_name'
        self.umapi_name = 'umapi_name'
        self.group_name = 'group_name'
        result = AdobeGroup.get_qualified_name(self)
        assert result == ("umapi_name::group_name")


    def test_parse(self):
        result = AdobeGroup._parse('qualified_name')
        assert result == ('qualified_name', None)

    def test_create(self):
        group = AdobeGroup.create('group_name')

        assert isinstance(group, AdobeGroup)
        assert group.get_group_name() == 'group_name'