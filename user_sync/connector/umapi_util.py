from user_sync.error import AssertionException
from Crypto.PublicKey import RSA
from user_sync.rsaencryptor import RSAEncryptor


def make_auth_dict(name, config, org_id, tech_acct, logger):
    auth_dict = {
        'org_id': org_id,
        'tech_acct_id': tech_acct,
        'api_key': config.get_credential('api_key', org_id),
        'client_secret': config.get_credential('client_secret', org_id),
    }
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
            key_data = RSAEncryptor.decrypt(passphrase, key_path)
        except (ValueError, IndexError, TypeError, AssertionException) as e:
            raise AssertionException('%s: Error decrypting private key, either the password is wrong or: %s' %
                                     (config.get_full_scope(), e))
    auth_dict['private_key_data'] = key_data
    return auth_dict
