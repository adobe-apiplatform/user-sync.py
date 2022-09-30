from sign_client.model import UserGroupsInfo
import json

def test_deserialize():
    """Test deserialization of a Sign API response"""
    # `widgetCreationVisible` is not part of the UserGroupsInfo
    # test will pass if user_groups_info is constructed with no errors

    # user permission info
    api_resp_json = """
    {
        "groupInfoList": [
            {
            "id": "",
            "isGroupAdmin": false,
            "isPrimaryGroup": false,
            "status": "",
            "createdDate": "date",
            "name": "",
            "settings": {
                "libaryDocumentCreationVisible": {
                    "value": false,
                    "inherited": false
                },
                "sendRestrictedToWorkflows": {
                    "value": false,
                    "inherited": false
                },
                "userCanSend": {
                    "value": false,
                    "inherited": false
                },
                "widgetCreationVisible": {
                    "value": false,
                    "inherited": false
                }
            }
            }
        ]
    }
    """
    dct = json.loads(api_resp_json)
    UserGroupsInfo.from_dict(dct)
