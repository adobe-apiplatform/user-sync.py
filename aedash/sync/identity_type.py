import aedash.sync.error
import aedash.sync.helper

ENTERPRISE_IDENTITY_TYPE = 'enterpriseID'
FEDERATED_IDENTITY_TYPE = 'federatedID'

NORMALIZED_IDENTITY_TYPE_MAP = {
    aedash.sync.helper.normalize_string(ENTERPRISE_IDENTITY_TYPE): ENTERPRISE_IDENTITY_TYPE,
    aedash.sync.helper.normalize_string(FEDERATED_IDENTITY_TYPE): FEDERATED_IDENTITY_TYPE
}

def parse_identity_type(value, message_format = None):
    '''
    :type value: str
    :type message_format: str
    :rtype str
    '''
    result = None
    if (value != None):
        normalized_value = aedash.sync.helper.normalize_string(value)
        result = NORMALIZED_IDENTITY_TYPE_MAP.get(normalized_value)
        if (result == None):
            validation_message = 'Unrecognized identity type: "%s"' % value
            message = validation_message if message_format == None else message_format % validation_message
            raise aedash.sync.error.AssertionException(message)
    return result

