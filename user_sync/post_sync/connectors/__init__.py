import importlib

_CONNECTOR_CLASSES = {
    'sign_sync': 'SignConnector'
}


def get_connector(connector_name, connector_config, test_mode):
    classname = _CONNECTOR_CLASSES[connector_name]
    class_ = getattr(importlib.import_module('.'+connector_name, package='user_sync.post_sync.connectors'), classname)
    return class_(connector_config, test_mode)
