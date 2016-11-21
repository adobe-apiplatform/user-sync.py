
UMAPI_CREDENTIAL_TYPE = "Adobe_UMAPI"
DIRECTORY_CREDENTIAL_TYPE = "Directory"

def get_credentials(credential_type, credential_id, **kwArgs):
    '''
    This allows a customer to customize how credentials are fetched.
    For the UMAPI related credential, the application will specify credential_type as "Adobe_UMAPI" and credential_id would 
    be the org id.
    For directory related credential like LDAP, the credential_type would be "Directory" and the credential_id would be 
    the type of directory connector like ldap, csv, etc.   
    kwArgs is a dictionary containing extra data, with:
    - 'config' being the current config for the credential to retrieve.
    - 'config_loader' being the instance of the loader
    
    The application supports these return types:
    - config object in dict
    - file path to a yaml file containing a config object
    - None
    
    :type credential_type: str
    :type id: str
    :type kwArgs: dict
    :rtype dict | str | None
    '''
    return None
    
