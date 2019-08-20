from .sign_sync import SignConnector

_CONNECTOR_CLASSES = {
    'sign_sync': SignConnector
}


def get_connector(connector_name, connector_config):
    connector = _CONNECTOR_CLASSES[connector_name]
    return connector(connector_config)
