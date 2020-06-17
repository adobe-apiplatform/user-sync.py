from user_sync.post_sync.connectors.sign_sync.__init__ import SignConnector


def test_should_sync():
    client_config = {
        'console_org': None,
        'host': 'api.na2.echosignstage.com',
        'key': 'examplekey',
        'admin_email': 'admin@example.com'
    }
    config = {'sign_orgs': [client_config], 'entitlement_groups': ['example product profile']}
    sc = SignConnector(config)
    umapi_user = {'type': 'adobeID', 'groups': ['example product profile_76TT88T-provisioning']}
    assert sc.should_sync(umapi_user, {}, None)
    umapi_user['groups'] = ['example product profile', 'other profile']
    assert sc.should_sync(umapi_user, {}, None)
    umapi_user['groups'] = ['other profile']
    assert sc.should_sync(umapi_user, {}, None) == set()
