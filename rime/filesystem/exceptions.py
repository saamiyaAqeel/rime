class NotDecryptedError(Exception):
    "Error to throw when the Filesystem is not decrypted."

    def __init__(self):
        self.message = "Filesystem is encrypted and cannot be read!"
        super().__init__(self.message)


class NoPassphraseError(Exception):
    "Error to throw when trying to decrypt without providing a passphrase."

    def __init__(self):
        self.message = "Cannot decrypt. Passphrase not provided!"
        super().__init__(self.message)


class WrongPassphraseError(Exception):
    "Error to throw when trying to decrypt with a wrong passphrase."

    def __init__(self):
        self.message = "Cannot decrypt. Passphrase is wrong!"
        super().__init__(self.message)
