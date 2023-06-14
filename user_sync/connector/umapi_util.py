from user_sync.error import AssertionException
from user_sync.encryption import decrypt
from umapi_client import JWTAuth, OAuthS2S


def create_umapi_auth(name, config, org_id, tech_acct, auth_host, auth_endpoint, ssl_verify, auth_type, logger):
    api_field = 'client_id' if 'client_id' in config or 'secure_client_id_key' in config else "api_key"
    if "api_key" in config and "client_id" in config:
        #word to be the same thing--take out api key--
        raise AssertionException('Cannot contain setting for both "api_key" and "client_id"(both fields set the same value). Please use "client_id."')
    if "api_key" in config and "secure_client_id" in config:
        raise AssertionException('Cannot contain setting for both "api_key" and "secure_client_id_key"(both fields set the same value). Please use "secure_client_id_key"')

    if auth_type == 'oauth':
        return OAuthS2S(
            client_id=config.get_credential(api_field, org_id),
            client_secret=config.get_credential('client_secret', org_id),
            auth_host=auth_host,
            auth_endpoint=auth_endpoint,
            ssl_verify=ssl_verify,
        )

    # get the private key
    key_path = config.get_string('priv_key_path', True)
    if key_path:
        data_setting = config.has_credential('priv_key_data')
        if data_setting:
            raise AssertionException('%s: cannot specify both "priv_key_path" and "%s"' %
                                     (config.get_full_scope(), data_setting))
        logger.debug('%s: reading private key data from file %s', name, key_path)
        try:
            with open(key_path, 'r') as f:
                key_data = f.read()
        except IOError as e:
            raise AssertionException('%s: cannot read file "%s": %s' %
                                     (config.get_full_scope(), key_path, e))
    else:
        key_data = config.get_credential('priv_key_data', org_id)
    # decrypt the private key, if needed
    passphrase = config.get_credential('priv_key_pass', org_id, True)
    if passphrase:
        try:
            key_data = decrypt(passphrase, key_data)
        except (ValueError, IndexError, TypeError, AssertionException) as e:
            raise AssertionException('%s: Error decrypting private key, either the password is wrong or: %s' %
                                     (config.get_full_scope(), e))

    return JWTAuth(
        org_id=org_id,
        client_id=config.get_credential(api_field, org_id),
        client_secret=config.get_credential('client_secret', org_id),
        tech_acct_id=tech_acct,
        priv_key_data=key_data,
        auth_host=auth_host,
        auth_endpoint=auth_endpoint,
        ssl_verify=ssl_verify,
    )
