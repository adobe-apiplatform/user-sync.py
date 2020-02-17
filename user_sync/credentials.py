import keyring


class CredentialManager:
    def __init__(self):
        pass

    def get(self, service_name, username):
        keyring.get_password(service_name, username)

    def set(self, service_name, username, password):
        try:
            keyring.set_password(service_name, username, password)
            print("password stored successfully")
        except keyring.errors.PasswordSetError:
            print("failed to store password")
