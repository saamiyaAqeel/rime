from .filesystem import DeviceFilesystem
from .session import Session
from .provider import find_providers


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

    def __repr__(self):
        return f"Device({self.id_})"
