# This software is released under the terms of the GNU GENERAL PUBLIC LICENSE.
# See LICENSE.txt for full details.
# Copyright 2023 Telemarq Ltd

from abc import ABC, abstractmethod
import hashlib
import os
import plistlib
import re
import sqlite3
import shutil
import zipfile
import tempfile

from .sql import Table, Query, get_field_indices, sqlite3_connect as sqlite3_connect_with_regex_support

import fs.osfs
import fs.tempfs


from logging import getLogger
log = getLogger(__name__)


class Error(Exception):
    pass


class FilesystemNotFoundError(Error):
    pass


class FilesystemTypeUnknownError(Error):
    pass


class FilesystemIsEncryptedError(Error):
    pass


class DeviceSettings:
    def __init__(self, path, settings_filename='_rime_settings.db'):
        self._db_name = os.path.join(path, settings_filename)
        self.conn = sqlite3_connect_with_regex_support(self._db_name)
        self._init_tables()

    def _init_tables(self):
        self.conn.execute("CREATE TABLE IF NOT EXISTS settings (key TEXT, value TEXT)")

    def _get_setting(self, key):
        c = self.conn.cursor()
        c.execute("SELECT value FROM settings WHERE key=?", (key,))
        row = c.fetchone()
        if row:
            return row[0]
        else:
            return None

    def _set_setting(self, key, value):
        c = self.conn.cursor()
        c.execute("UPDATE settings SET value=? WHERE key=?", (value, key))
        if c.rowcount == 0:
            c.execute("INSERT INTO settings (key, value) VALUES (?, ?)", (key, value))
        self.conn.commit()

    def is_subset_fs(self):
        return self._get_setting('subset_fs') == '1'

    def set_subset_fs(self, is_subset_fs):
        self._set_setting('subset_fs', '1' if is_subset_fs else '0')

    def is_locked(self):
        return self._get_setting('locked') == '1'

    def set_locked(self, is_locked):
        self._set_setting('locked', '1' if is_locked else '0')


def _ensuredir(pathname):
    dirname = os.path.dirname(pathname)
    if not os.path.exists(dirname):
        os.makedirs(dirname)


class DeviceFilesystem(ABC):
    @classmethod
    @abstractmethod
    def is_device_filesystem(cls, path) -> bool:
        """
        Is this path the root of a filesystem this class can manage?
        """
        return False

    @classmethod
    @abstractmethod
    def create(cls, id_: str, root: str) -> 'DeviceFilesystem':
        """
        Create a new filesystem of this type at 'path'.
        """
        raise NotImplementedError()

    @abstractmethod
    def is_subset_filesystem(self) -> bool:
        """
        Is this a temporary filesystem?
        """
        return False

    @abstractmethod
    def listdir(self, path) -> list[str]:
        """
        As os.listdir().
        """
        return []

    @abstractmethod
    def exists(self, path) -> bool:
        """
        As os.path.exists().
        """
        return False

    @abstractmethod
    def getsize(self, path) -> int:
        """
        As os.path.getsize().
        """
        return 0

    @abstractmethod
    def open(self, path):
        """
        As open().
        """
        return None

    @abstractmethod
    def create_file(self, path):
        """
        As open(path, 'wb').
        """
        return None

    def sqlite3_uri(self, path, read_only=True):
        """
        Return a URI suitable for passing to sqlite3_connect
        """
        params = "?mode=ro&immutable=1" if read_only else ""
        return f"file:{path}{params}"

    @abstractmethod
    def sqlite3_connect(self, path, read_only=True):
        """
        Return an opened sqlite3 connection to the database at 'path'.
        """
        return None

    @abstractmethod
    def sqlite3_create(self, path):
        """
        Create a new sqlite3 database at 'path' and return an opened connection read-write to it.
        """
        return None

    @abstractmethod
    def lock(self, locked: bool):
        """
        Lock or unlock the filesystem. A locked filesystem can't be viewed or written to.
        """
        pass

    @abstractmethod
    def is_locked(self) -> bool:
        """
        Is the filesystem locked?
        """
        return False


class AndroidDeviceFilesystem(DeviceFilesystem):
    def __init__(self, id_: str, root: str):
        self.id_ = id_
        self._fs = fs.osfs.OSFS(root)
        self._settings = DeviceSettings(root)

    @classmethod
    def is_device_filesystem(cls, path):
        return os.path.exists(os.path.join(path, 'data', 'data', 'android'))

    @classmethod
    def create(cls, id_: str, root: str):
        if os.path.exists(root):
            raise FileExistsError(root)

        os.makedirs(root)
        os.makedirs(os.path.join(root, 'data', 'data', 'android'))

        obj = cls(id_, root)
        obj._settings.set_subset_fs(True)
        return obj

    def is_subset_filesystem(self) -> bool:
        return self._settings.is_subset_fs()

    def listdir(self, path):
        return self._fs.listdir(path)

    def exists(self, path):
        return self._fs.exists(path)

    def getsize(self, path):
        return self._fs.getsize(path)

    def open(self, path):
        return self._fs.open(path, 'rb')

    def create_file(self, path):
        _ensuredir(self._fs.getsyspath(path))

        return self._fs.open(path, 'wb')

    def sqlite3_connect(self, path, read_only=True):
        db_url = self.sqlite3_uri(self._fs.getsyspath(path), read_only)
        log.debug(f"Android connecting to {db_url}")
        return sqlite3_connect_with_regex_support(db_url, uri=True)

    def sqlite3_create(self, path):
        syspath = self._fs.getsyspath(path)

        _ensuredir(syspath)
        return sqlite3_connect_with_regex_support(syspath)

    def lock(self, locked: bool):
        self._settings.set_locked(locked)

    def is_locked(self) -> bool:
        return self._settings.is_locked()


class AndroidZippedDeviceFilesystem(DeviceFilesystem):
    """
    Zipped filesystem of an Android device. Currently supports only read mode
    for the data.

    The class assumes that there is one directory in the .zip file
    and all the other files and directories are located withn that directory.

        file.zip
            |- main_dir
                |- _rime_settings.db
                |- sdcard
                    |- ...
                |- data
                    |- ...

    The contents of the .zip file are extracted in a temporary directory
    and then the (only) directory from within the temporary directory
    (the `main_dir`) is used to instantiate a filesystem. All queries
    refer to the data in the temporary directory.
    """

    def __init__(self, id_: str, root: str):
        self.id_ = id_

        # extract the files from the zipfile in a temporary directory
        self.temp_root = tempfile.TemporaryDirectory()

        with zipfile.ZipFile(root) as zp:
            zp.extractall(path=self.temp_root.name)
            main_dir, = zipfile.Path(zp).iterdir()

        # instantiate a filesystem from the temporary directory
        self._fs = fs.osfs.OSFS(os.path.join(self.temp_root.name, main_dir.name))
        self._settings = DeviceSettings(os.path.join(self.temp_root.name, main_dir.name))

    @classmethod
    def is_device_filesystem(cls, path):

        if not zipfile.is_zipfile(path):
            return False

        with zipfile.ZipFile(path) as zp:
            # get the main directory contained in the .zip container file
            main_dir, = zipfile.Path(zp).iterdir()
            return zipfile.Path(zp, os.path.join(main_dir.name, 'data', 'data', 'android/'))

    @classmethod
    def create(cls, id_: str, root: str):
        raise NotImplementedError

    def is_subset_filesystem(self) -> bool:
        return self._settings.is_subset_fs()

    def listdir(self, path):
        return self._fs.listdir(path)

    def exists(self, path):
        return self._fs.exists(path)

    def getsize(self, path):
        return self._fs.getsize(path)

    def open(self, path):
        return self._fs.open(path, 'rb')

    def create_file(self, path):
        raise NotImplementedError

    def sqlite3_connect(self, path, read_only=True):
        db_url = self.sqlite3_uri(self._fs.getsyspath(path), read_only)
        log.debug(f"Android connecting to {db_url}")
        return sqlite3_connect_with_regex_support(db_url, uri=True)

    def sqlite3_create(self, path):
        raise NotImplementedError

    def lock(self, locked: bool):
        self._settings.set_locked(locked)

    def is_locked(self) -> bool:
        return self._settings.is_locked()


class _IosHashedFileConverter:
    def __init__(self, manifest_conn):
        self.manifest_conn = manifest_conn
        self.file_table = Table('Files')

    @staticmethod
    def _get_ios_hash(domain, relative_path):
        # Construct a hashable path from the domain and relative path.
        # The string used for hashing is of the form domain-relativePath, i.e. the same as 'path' with the first
        # slash replaced with a hyphen. We don't use this form in the rest of RIME because domains can contain hyphens,
        # so we wouldn't know where to split.
        hashable_path = f"{domain}-{relative_path}"

        return hashlib.sha1(hashable_path.encode()).hexdigest()

    def get_hashed_pathname(self, path):
        """
        Return the pathname inside an iOS backup of path 'path'. Used by providers when accessing iOS files.

        path is of the form domain/relativePath.

        For example, the SMS database, in domain HomeDomain and with relative path Library/SMS/sms.db, is
        referenced by the path HomeDomain/Library/SMS/sms.db.
        """
        # TODO: some files are stored in blobs in the manifest. Need to deal with that.
        domain, relative_path = path.split('/', 1)

        # First, attempt to look up the file in the manifest.
        query = Query.from_(self.file_table).select('fileID')\
            .where(self.file_table.domain == domain)\
            .where(self.file_table.relativePath == relative_path)

        try:
            result = self.manifest_conn.execute(str(query)).fetchone()
        except sqlite3.OperationalError:
            result = None

        if result:
            file_id = result[0]
        else:
            file_id = self._get_ios_hash(domain, relative_path)

        return os.path.join(file_id[:2], file_id)

    def add_file(self, path):
        """
        Add a file to Manifest.db. It's okay to add the same file twice (only one entry will be created).

        Raises FileExistsError if an entry for a different 'path' exists with the same hash.
        """
        domain, relative_path = path.split('/', 1)
        ios_hash = self._get_ios_hash(domain, relative_path)

        query = Query.from_(self.file_table).select(self.file_table.relativePath, self.file_table.domain)\
            .where(self.file_table.fileID == ios_hash)

        result = self.manifest_conn.execute(str(query)).fetchone()

        if not result:
            # File not in database.
            query = Query.into(self.file_table)\
                .columns(self.file_table.fileID, self.file_table.domain, self.file_table.relativePath)\
                .insert(ios_hash, domain, relative_path)

            self.manifest_conn.execute(str(query))

            self.manifest_conn.commit()
        elif not (result[0] == relative_path and result[1] == domain):
            # File hash in database, but for a different file.
            raise FileExistsError(path)

        # If we get here, the hash and matching path are already in the database, which is fine.


def _ios_filesystem_is_encrypted(path):
    manifest_bplist = os.path.join(path, 'Manifest.plist')
    if not os.path.exists(manifest_bplist):
        return False

    with open(manifest_bplist, 'rb') as f:
        manifest = plistlib.load(f)

    return manifest.get('IsEncrypted', False)


class IosDeviceFilesystem(DeviceFilesystem):
    def __init__(self, id_: str, root: str):
        self.id_ = id_
        self.root = root
        self.manifest = sqlite3_connect_with_regex_support(os.path.join(self.root, 'Manifest.db'))
        self.file_table = Table('Files')
        self._settings = DeviceSettings(root)
        self._converter = _IosHashedFileConverter(self.manifest)

    @classmethod
    def is_device_filesystem(cls, path):
        return (
            os.path.exists(os.path.join(path, 'Manifest.db'))
            and os.path.exists(os.path.join(path, 'Info.plist'))
            and not _ios_filesystem_is_encrypted(path)
        )

    @classmethod
    def create(cls, id_: str, root: str):
        if os.path.exists(root):
            raise FileExistsError(root)

        os.makedirs(root)

        for filename in {'Manifest.db', 'Info.plist'}:
            with open(os.path.join(root, filename), 'wb'):
                pass  # touch the file to ensure it exists

        obj = cls(id_, root)
        obj._settings.set_subset_fs(True)
        return obj

    def is_subset_filesystem(self) -> bool:
        return self._settings.is_subset_fs()

    def sqlite3_connect(self, path, read_only=True):
        db_url = self.sqlite3_uri(os.path.join(self.root, self._converter.get_hashed_pathname(path)), read_only)
        log.debug(f"iOS connecting to {db_url} ({path})")
        return sqlite3_connect_with_regex_support(db_url, uri=True)

    def listdir(self, path):
        query = Query.from_(self.file_table).select('fileID', 'relativePath')
        query = query.where(self.file_table.relativePath == os.path.join(self.root, path))
        fields = get_field_indices(query)
        return [row[fields['relativePath']] for row in self.manifest.execute(str(query))]

    def exists(self, path):
        real_path = self._converter.get_hashed_pathname(path)
        return os.path.exists(os.path.join(self.root, real_path))

    def getsize(self, path):
        return os.path.getsize(os.path.join(self.root, self._converter.get_hashed_pathname(path)))

    def open(self, path):
        # TODO: Should cope with blobs in the manifest too
        return open(os.path.join(self.root, self._converter.get_hashed_pathname(path), 'rb'))

    def create_file(self, path):
        raise NotImplementedError

    def sqlite3_create(self, path):
        """
        Create a new sqlite3 database at the given path and fail if it already exists.
        """
        self._converter.add_file(path)

        real_path = self._converter.get_hashed_pathname(path)
        syspath = os.path.join(self.root, real_path)

        if self.exists(syspath):
            raise FileExistsError(path)

        _ensuredir(syspath)

        return sqlite3_connect_with_regex_support(syspath)

    def lock(self, locked: bool):
        self._settings.set_locked(locked)

    def is_locked(self) -> bool:
        return self._settings.is_locked()


class IosZippedDeviceFilesystem(DeviceFilesystem):
    """
    Zipped filesystem of an iOS device. Currently supports only read mode
    for the data.

    The class assumes there is only one directory in the .zip file
    and all the other files and directories are located withn that directory.

        file.zip
            |- main_dir
                |- Manifest.db
                |- Info.plist
                |- 7c
                    |- 7c7fba66680ef796b916b067077cc246adacf01d
    """

    @staticmethod
    def get_main_dir(zp: zipfile.ZipFile) -> zipfile.Path:
        """
        Get the main directory from within the zip file. The zip file
        should contain one directory and all other files should be in
        that directory.
        """
        root = zipfile.Path(zp)
        main_dir, = root.iterdir()
        return main_dir

    def __init__(self, id_: str, root: str):
        self.id_ = id_

        # store the path of the root for other functions
        # to be able to open the zipfile
        self.root = root

        # keep a reference to the tempfile in the object
        self.temp_manifest = tempfile.NamedTemporaryFile(mode='w+b')
        self.temp_settings = tempfile.NamedTemporaryFile(mode='w+b')

        with zipfile.ZipFile(self.root) as zp:
            # get the main directory contained in the .zip container file
            main_dir = self.get_main_dir(zp)

            with zp.open(os.path.join(main_dir.name, 'Manifest.db')) as zf:
                self.temp_manifest.write(zf.read())

            with zp.open(os.path.join(main_dir.name, '_rime_settings.db')) as zf:
                self.temp_settings.write(zf.read())

        self.manifest = sqlite3_connect_with_regex_support(self.temp_manifest.name)
        self.file_table = Table('Files')

        settings_dir, settings_file = os.path.split(self.temp_settings.name)
        self._settings = DeviceSettings(settings_dir, settings_file)
        self._converter = _IosHashedFileConverter(self.manifest)

    @classmethod
    def is_device_filesystem(cls, path) -> bool:

        if not zipfile.is_zipfile(path):
            return False

        with zipfile.ZipFile(path) as zp:
            # get the main directory contained in the .zip container file
            main_dir = cls.get_main_dir(zp)
            return (
                zipfile.Path(zp, os.path.join(main_dir.name, 'Manifest.db')).exists()
                and zipfile.Path(zp, os.path.join(main_dir.name, 'Info.plist')).exists()
            )

    @classmethod
    def create(cls, id_: str, root: str):
        raise NotImplementedError

    def is_subset_filesystem(self) -> bool:
        return self._settings.is_subset_fs()

    def listdir(self, path) -> list[str]:
        raise NotImplementedError

    def exists(self, path) -> bool:

        real_path = self._converter.get_hashed_pathname(path)

        # open the zipfile stored in `self.root` and find out if it
        # contains the `real_path
        with zipfile.ZipFile(self.root) as zp:
            # get the main directory contained in the .zip container file
            main_dir = self.get_main_dir(zp)
            return zipfile.Path(zp, os.path.join(main_dir.name, real_path)).exists()

    def getsize(self, path) -> int:
        with zipfile.ZipFile(self.root) as zp:
            # get the main directory contained in the .zip container file
            main_dir = self.get_main_dir(zp)
            return zp.getinfo(os.path.join(main_dir, self._converter.get_hashed_pathname(path))).file_size

    def open(self, path):
        tmp_copy = tempfile.NamedTemporaryFile(mode='w+b')
        with zipfile.ZipFile(self.root) as zp:
            # get the main directory contained in the .zip container file
            main_dir = self.get_main_dir(zp)
            with zp.open(os.path.join(main_dir.name, self._converter.get_hashed_pathname(path))) as zf:
                tmp_copy.write(zf.read())
        return tmp_copy

    def create_file(self, path):
        raise NotImplementedError

    def sqlite3_uri(self, path, read_only=True):
        params = "?mode=ro&immutable=1" if read_only else ""
        return f"file:{path}{params}"

    def sqlite3_connect(self, path, read_only=True):
        tmp_copy = tempfile.NamedTemporaryFile(mode='w+b')

        with zipfile.ZipFile(self.root) as zp:
            # get the main directory contained in the .zip container file
            main_dir = self.get_main_dir(zp)
            with zp.open(os.path.join(main_dir.name, self._converter.get_hashed_pathname(path))) as zf:
                tmp_copy.write(zf.read())

        db_url = self.sqlite3_uri(tmp_copy.name)
        log.debug(f"iOS connecting to {db_url} ({path})")
        return sqlite3_connect_with_regex_support(db_url, uri=True)

    def sqlite3_create(self, path):
        raise NotImplementedError

    def lock(self, locked: bool):
        self._settings.set_locked(locked)

        # update the settings file back in the zipped file
        # for persistent settings preferenses
        with zipfile.ZipFile(self.root, 'w') as zp:
            # get the main directory contained in the .zip container file
            main_dir = self.get_main_dir(zp)
            with zp.open(os.path.join(main_dir, '_rime_settings.db'), 'w') as zf:
                zf.write(self.temp_settings.read())

    def is_locked(self) -> bool:
        return self._settings.is_locked()


class IosEncryptedDeviceFilesystem(DeviceFilesystem):
    def __init__(self, id_: str, root: str):
        self.id_ = id_
        self.root = root

    @classmethod
    def is_device_filesystem(cls, path):
        return (
            os.path.exists(os.path.join(path, 'Manifest.db'))
            and os.path.exists(os.path.join(path, 'Info.plist'))
            and _ios_filesystem_is_encrypted(path)
        )

    @classmethod
    def create(cls, id_: str, root: str) -> 'DeviceFilesystem':
        return cls(id_, root)

    def is_subset_filesystem(self) -> bool:
        return False

    def listdir(self, path) -> list[str]:
        return []

    def exists(self, path) -> bool:
        return False

    def getsize(self, path) -> int:
        raise NotImplementedError

    def open(self, path):
        raise NotImplementedError

    def create_file(self, path):
        raise NotImplementedError

    def sqlite3_uri(self, path, read_only=True):
        raise NotImplementedError

    def sqlite3_connect(self, path, read_only=True):
        raise NotImplementedError

    def sqlite3_create(self, path):
        raise NotImplementedError

    def lock(self, locked: bool):
        raise NotImplementedError

    def is_locked(self) -> bool:
        return True


FILESYSTEM_TYPE_TO_OBJ = {
    'android': AndroidDeviceFilesystem,
    'android-zipped': AndroidZippedDeviceFilesystem,
    'ios': IosDeviceFilesystem,
    'ios-zipped': IosZippedDeviceFilesystem,
    'ios-encrypted': IosEncryptedDeviceFilesystem,
}


VALID_DEVICE_ID_REGEX = re.compile(r'^[a-zA-Z0-9_-]+$')


class FilesystemRegistry:
    """
    Maintains a registry of filesystems at 'base_path'.

    Filesystems are distinguished by a key, which is the name of the directory they're in under base_path.
    """
    def __init__(self, base_path):
        self.base_path = base_path
        self.filesystems = self._find_available_filesystems()  # maps key to FS object.

    def __getitem__(self, key):
        return self.filesystems[key]

    def rescan(self):
        self.filesystems = self._find_available_filesystems()

    def _find_available_filesystems(self):
        """
        Return a mapping of key -> filesystem type for each valid filesystem under base_path.
        """
        filesystems = {}

        try:
            for filename in os.listdir(self.base_path):
                path = os.path.join(self.base_path, filename)

                for fs_cls in FILESYSTEM_TYPE_TO_OBJ.values():
                    if fs_cls.is_device_filesystem(path):
                        filesystems[filename] = fs_cls(filename, path)
        except FileNotFoundError:
            log.warning(f"Could not find filesystem directory: {self.base_path}")

        return filesystems

    def create_empty_subset_of(self, fs: DeviceFilesystem, key: str, locked: bool = False) -> DeviceFilesystem:
        """
        Create an empty subset filesystem of the same type as 'fs' named 'key'
        """
        path = os.path.join(self.base_path, key)

        if os.path.exists(path):
            raise FileExistsError(key)

        if not self.is_valid_device_id(key):
            raise ValueError(f"Invalid device ID: {key}")

        self.filesystems[key] = fs.__class__.create(key, path)
        print('locked', locked)
        self.filesystems[key].lock(locked)

        return self[key]

    def is_valid_device_id(self, key):
        return VALID_DEVICE_ID_REGEX.match(key)

    def delete(self, key):
        if key not in self.filesystems:
            raise FileNotFoundError(key)

        shutil.rmtree(os.path.join(self.base_path, key))
        del self.filesystems[key]
