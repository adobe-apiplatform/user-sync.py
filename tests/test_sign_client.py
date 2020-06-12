import json
from unittest import mock
from requests import Response
from user_sync.post_sync.connectors.sign_sync.client import SignClient


@mock.patch('requests.get')
@mock.patch('user_sync.post_sync.connectors.sign_sync.client.SignClient._init')
def test_get_users(mock_client, mock_get):
    def mock_response(data):
        r = Response()
        r.status_code = 200
        r._content = json.dumps(data).encode()
        return r
    config = {
        'console_org': None,
        'host': 'example.com',
        'key': '1234567890',
        'admin_email': 'example@example.com'
    }
    user_list = mock_response({'userInfoList': [{"userId": "active"}, {"userId": "inactive"}, {"userId": "nostatus"}]})
    active_user = mock_response({'userStatus': 'ACTIVE', 'email': 'active@example.com'})
    inactive_user = mock_response({'userStatus': 'INACTIVE', 'email': 'inactive@example.com'})
    no_status_user = mock_response({'email': 'nostatus@example.com'})

    mock_get.side_effect = [user_list, active_user, inactive_user, no_status_user]
    sc = SignClient(config)
    sc.api_url = "example.com"
    users = sc.get_users()
    assert 'active@example.com' and 'nostatus@example.com' in users
    assert 'inactive@example.com' not in users
