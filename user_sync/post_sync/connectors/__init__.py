from .sign_sync import connector_sign

__CONNECTORS__ = {
    'sign_sync': connector_sign.SignConnector
}


def get_connector(connector_name, connector_config):
    connector = __CONNECTORS__[connector_name]
    return connector(connector_config)
