import logging

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

