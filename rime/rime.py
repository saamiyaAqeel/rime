# This software is released under the terms of the GNU GENERAL PUBLIC LICENSE.
# See LICENSE.txt for full details.
# Copyright 2023 Telemarq Ltd

import threading

from .providers import find_providers
from .filesystem import FilesystemRegistry, DeviceFilesystem
from .session import Session
from .graphql import query as _graphql_query
from .config import Config
from .plugins import load_plugin
from .pubsub import broker, Scheduler


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


FILESYSTEM_REGISTRY = threading.local()
DEVICE_CACHE = threading.local()
RIME = threading.local()


class Rime:
    """
    Top-level RIME object.

    Contains per-device sub-objects.
    """
    def __init__(self, session: Session, constants: Config, scheduler: Scheduler):
        self.devices = []
        self.session = session
        self.constants = constants
        self.scheduler = scheduler
        media_prefix = constants.get('media_url_prefix', '/media/')

        self.rescan_devices()

        self.media_prefix = media_prefix
        self.plugins = self._load_plugins()

        broker.subscribe('devices_changed', self._devices_changed)

    def _devices_changed(self, *args):
        # Callback from broker; ensure we do the device rescan on our own thread as it will close and open
        # DB connections.
        self.scheduler.run_on_my_thread(lambda: Rime.get().rescan_devices())

    def rescan_devices(self):
        registry = FILESYSTEM_REGISTRY.registry
        registry.rescan()

        if not hasattr(DEVICE_CACHE, 'devices'):
            DEVICE_CACHE.devices = [Device(fs_id, fs, self.session) for fs_id, fs in registry.filesystems.items()]

        self.devices = DEVICE_CACHE.devices
        self._device_for_id = {device.id_: device for device in self.devices}

    def devices_for_ids(self, device_ids: list[str]) -> list[Device]:
        return [device for device in self.devices if device.id_ in device_ids]

    def device_for_id(self, device_id: str) -> Device:
        return self._device_for_id[device_id]

    def has_device(self, device_id: str) -> bool:
        return any(device.id_ == device_id for device in self.devices)

    def create_empty_subset_of(self, device, new_device_id, locked=True):
        if any(new_device_id == device.id_ for device in self.devices):
            raise ValueError(f"Device ID {new_device_id} already exists")

        new_fs = self.filesystem_registry.create_empty_subset_of(device.fs, new_device_id, locked=locked)
        new_device = Device(new_device_id, new_fs, self.session)
        self.devices.append(new_device)

        return new_device

    def delete_device(self, device_id: str):
        devices_remaining = []
        for device in self.devices:
            if device.id_ == device_id:
                self.filesystem_registry.delete(device_id)
            else:
                devices_remaining.append(device)

        did_delete = len(devices_remaining) != len(self.devices)

        self.devices = devices_remaining
        self._device_for_id = {device.id_: device for device in self.devices}

        return did_delete

    def query(self, query_json: dict):
        return _graphql_query(self, query_json)

    def get_media(self, media_path):
        """
        Return (handle, content-type)

        where 'handle' is a file-like object representing the media, and 'content-type' is a string
        """
        device_id, provider_name, local_id = media_path.split(':', 2)

        device = self.device_for_id(device_id)
        provider = device.providers[provider_name]

        return provider.get_media(local_id)

    def get_constant(self, path: list[str], default):
        if not isinstance(path, list):
            raise ValueError("path must be a list")

        val = self.constants
        for key in path[:-1]:
            if key not in val:
                return default
            val = val[key]

        return val.get(path[-1], default)

    @property
    def filesystem_registry(self) -> FilesystemRegistry:
        return FILESYSTEM_REGISTRY.registry

    @classmethod
    def create(cls, config: Config, scheduler: Scheduler):
        if hasattr(RIME, 'rime'):
            raise RuntimeError("Rime already created on this thread")

        if not hasattr(FILESYSTEM_REGISTRY, 'registry'):
            FILESYSTEM_REGISTRY.registry = FilesystemRegistry(base_path=config.get_pathname('filesystem.base_path'))

        session = Session(config.get_pathname('session.database'))
        obj = cls(session, config, scheduler)

        RIME.rime = obj
        return obj

    @classmethod
    def get(cls):
        return RIME.rime

    def _load_plugins(self):
        plugins = {}
        for category, plugin_list in self.constants.get('plugins', {}).items():
            if not plugin_list:
                continue

            plugins[category] = []
            for plugin_name in plugin_list:
                plugins[category].append(load_plugin(category, plugin_name))

        return plugins
