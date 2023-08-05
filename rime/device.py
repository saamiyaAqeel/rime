from .filesystem import DeviceFilesystem
from .session import Session
from .provider import find_providers
from .errors import NotEncryptedDeviceType


class Device:
    def __init__(self, device_id: str, fs: DeviceFilesystem, session: Session):
        self.id_ = device_id
        self.fs = fs
        self.providers = find_providers(self.fs)
        self.session = session

    def reload_providers(self):
        self.providers = find_providers(self.fs)

    @property
    def country_code(self) -> str:
        return self.session.get_device_country_code(self.id_, 'GB')

    @country_code.setter
    def country_code(self, value: str):
        self.session.set_device_country_code(self.id_, value)

    def is_subset(self) -> bool:
        return self.fs.is_subset_filesystem()

    def is_locked(self) -> bool:
        return self.fs.is_locked()

    def lock(self, locked):
        self.fs.lock(locked)

    def _is_encrypted_device_type(self) -> bool:
        return 'Encrypted' in self.fs.__class__.__name__

    def is_encrypted(self) -> bool:
        return (self._is_encrypted_device_type() and self.fs.is_encrypted())

    def decrypt(self, passphrase: str) -> bool:
        """
        Try to decrypt device with provided passphrase. Return:
            - True when decryption is successful
            - False when decryption is not successful
        """

        if not self._is_encrypted_device_type():
            raise NotEncryptedDeviceType

        try:
            self.fs.decrypt(passphrase)
            self.reload_providers()
            return True

        except WrongPassphraseError:
            print('Failed to decrypt with provided passphrase.')
            return False

    def __repr__(self):
        return f"Device({self.id_})"
