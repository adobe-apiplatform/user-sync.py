from user_sync.error import AssertionException
from user_sync.encryption import decrypt


def make_auth_dict(name, config, org_id, tech_acct, logger):
    auth_dict = {
        'org_id': org_id,
        'tech_acct_id': tech_acct,
        'api_key': config.get_credential('api_key', org_id),
        'client_secret': config.get_credential('client_secret', org_id),
    }
    key_data = get_key_data(name, config, org_id, logger)
    # decrypt the private key, if needed
    passphrase = config.get_credential('priv_key_pass', org_id, True)
    if passphrase:
        try:
            key_data = decrypt(passphrase, key_data)
        except (ValueError, IndexError, TypeError, AssertionException) as e:
            raise AssertionException('%s: Error decrypting private key, either the password is wrong or: %s' %
                                     (config.get_full_scope(), e))
    auth_dict['private_key_data'] = key_data
    return auth_dict


def get_key_data(name, config, org_id, logger):
    key_path = config.get_string('priv_key_path', True)
    data_setting = config.get_value('priv_key_data', (str, dict), True)
    secure_data_setting = config.get_string(config.keyring_prefix + 'priv_key_data' + config.keyring_suffix, True)
    if key_path and data_setting:
        raise AssertionException('%s: cannot specify both "priv_key_path" and "%s"' %
                                 (config.get_full_scope(), data_setting))
    elif key_path and secure_data_setting:
        raise AssertionException('%s: cannot specify both "priv_key_path" and "%s"' %
                                 (config.get_full_scope(), secure_data_setting))
    elif key_path is not None:
        logger.debug('%s: reading private key data from file %s', name, key_path)
        try:
            with open(key_path, 'r') as f:
                key_data = f.read()
        except IOError as e:
            raise AssertionException('%s: cannot read file "%s": %s' %
                                     (config.get_full_scope(), key_path, e))
    else:
        try:
            # this covers the case of having both the plaintext and secure format for priv_key_data
            key_data = config.get_credential('priv_key_data', org_id)
        except AssertionException as e:
            raise e
    return key_data
