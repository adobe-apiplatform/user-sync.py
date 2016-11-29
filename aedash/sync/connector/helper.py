import logging

import aedash.sync.error
         
def create_logger(options):
    '''
    :type options: dict
    '''        
    logger_name = options.get('logger_name')
    if (logger_name == None):
        logger_name = 'connector'
    return logging.getLogger(logger_name)
     
def create_blank_user():
    '''
    :rtype dict
    '''
    user = {
        "identitytype": None,
        "username": None,
        "domain": None,
        "firstname": None,
        "lastname": None,
        "email": None,
        "groups": [],
        "country": None,
    }
    return user;

def validate_options(options, required_option_names, message_format = None):
    '''
    :type options: dict
    :type required_option_names: list(str)
    '''        
    for required_option_name in required_option_names:
        names = required_option_name.split(".")
        scope = options
        for name in names:
            if isinstance(scope, dict) and (name in scope):
                scope = scope[name]
                if (scope != None):
                    continue
            validation_message = 'Setting not defined: "%s"' % required_option_name
            message = validation_message if message_format == None else message_format % validation_message
            raise aedash.sync.error.AssertionException(message)
            
