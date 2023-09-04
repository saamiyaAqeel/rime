# This software is released under the terms of the GNU GENERAL PUBLIC LICENSE.
# See LICENSE.txt for full details.
# Copyright 2023 Telemarq Ltd

from abc import ABC, abstractmethod
from dataclasses import dataclass
import hashlib
import os
import plistlib
import re
import sqlite3
import stat
import shutil
import zipfile
import tempfile

from iphone_backup_decrypt import EncryptedBackup

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

    def is_encrypted(self):
        return self._get_setting('encrypted') == '1'

    def set_encrypted(self, is_encrypted):
        self._set_setting('encrypted', '1' if is_encrypted else '0')


def _ensuredir(pathname):
    dirname = os.path.dirname(pathname)
    if not os.path.exists(dirname):
        os.makedirs(dirname)


@dataclass(frozen=True, unsafe_hash=True)
class DirEntry:
    """
    Mimic os.DirEntry for the scandir() method. Stores metadata at time of instantiation rather than
    querying the filesystem the first time (unlike os.DirEntry).
    """
    # Ideally we'd use os.DirEntry, but these can't be instantiated.
    name: str
    path: str
    stat_val: os.stat_result

    def is_dir(self):
        return stat.S_ISDIR(self.stat_val.st_mode)

    def is_file(self):
        return stat.S_ISREG(self.stat_val.st_mode)

    def stat(self):
        return self.stat_val


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
    def scandir(self, path) -> list[DirEntry]:
        """
        As os.scandir().
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


class EncryptedDeviceFilesystem(DeviceFilesystem):
    @abstractmethod
    def is_encrypted(self) -> bool:
        return False

    @abstractmethod
    def decrypt(self, passphrase: str) -> bool:
        pass


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

    def scandir(self, path):
        result = []
        for name in self._fs.listdir(path):
            pathname = os.path.join(path, name)  # I love it when a plan comes together
            syspath = self._fs.getsyspath(pathname)
            stat_val = os.stat(syspath)
            result.append(DirEntry(name, pathname, stat_val))

        return result

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
        return AndroidDeviceFilesystem.create(id_, root)

    def is_subset_filesystem(self) -> bool:
        return self._settings.is_subset_fs()

    def scandir(self, path):
        entries = []
        for name in self._fs.listdir(path):
            pathname = os.path.join(path, name)
            syspath = self._fs.getsyspath(pathname)
            statval = os.stat(syspath)
            entries.append(DirEntry(name, pathname, statval))

        return entries

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


class _IosManifest:
    def __init__(self, manifest_conn):
        self.manifest_conn = manifest_conn
        self.file_table = Table('Files')
        self._scandir_cache = {}

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

    def scandir(self, path):
        # Retrieving the contents of a directory from an iOS backup is hard, because the file stat info
        # is stored in a binary plist in the manifest, so cache the result.
        if path in self._scandir_cache:
            return self._scandir_cache[path]

        domain, relative_path = path.split('/', 1)

        query = Query.from_(self.file_table).select('fileID', 'relativePath', 'file')
        query = query.where(self.file_table.domain == domain)
        fields = get_field_indices(query)

        entries = []
        for row in self.manifest_conn.execute(str(query)):
            name = row[fields['relativePath']]

            if not name.startswith(relative_path):
                # Ignore files in directories above this one.
                continue

            if name[len(relative_path) + 1:].count('/') > 1:  # skip leading '/'
                # Ignore files in directories below this one.
                continue

            blob = row[fields['file']]
            blob_plist = plistlib.loads(blob)

            file_metadata = blob_plist['$objects'][1]

            stat_info = os.stat_result([
                file_metadata['Mode'],
                file_metadata['InodeNumber'],
                0,  # st_dev
                0,  # st_nlink
                file_metadata['UserID'],
                file_metadata['GroupID'],
                file_metadata['Size'],
                0,  # st_atime
                file_metadata['LastModified'],  # st_mtime
                file_metadata['Birth'],  # st_ctime
            ])

            entries.append(DirEntry(
                name=name,
                path=f'{path}/{name}',
                stat_val=stat_info
            ))

        self._scandir_cache[path] = entries
        return entries


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
        self._converter = _IosManifest(self.manifest)

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

        # Create Manifest for file hashing. Do this manually because we don't have a device yet.
        syspath = os.path.join(root, 'Manifest.db')

        with sqlite3_connect_with_regex_support(syspath) as conn:
            conn.execute("""CREATE TABLE Files (
                fileID TEXT PRIMARY KEY,
                domain TEXT,
                relativePath TEXT,
                flags INTEGER,
                file BLOB)
            """)
            conn.execute('CREATE TABLE Properties (key TEXT PRIMARY KEY, value BLOB)')

        # Create Info.plist.
        with open(os.path.join(root, 'Info.plist'), 'wb'):
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

    def scandir(self, path):
        return self._converter.scandir(path)

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
        self._converter = _IosManifest(self.manifest)

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
        return IosDeviceFilesystem.create(id_, root)

    def is_subset_filesystem(self) -> bool:
        return self._settings.is_subset_fs()

    def scandir(self, path) -> list[str]:
        return self._converter.scandir(path)

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


class IosEncryptedDeviceFilesystem(EncryptedDeviceFilesystem):

    decrypted_manifest_filename = 'Manifest-decrypted.db'

    def __init__(self, id_: str, root: str):
        self.id_ = id_
        self.root = root
        self.file_table = Table('Files')
        self._settings = DeviceSettings(root)

        # Check if the manifest exists already,
        # otherwise need to decrypt first to get the decrypted Manifest and a
        # _backup object that can be used to decrypt the requested SQLite3 file
        if os.path.exists(os.path.join(self.root, self.decrypted_manifest_filename)):
            self.manifest = sqlite3_connect_with_regex_support(
                os.path.join(self.root,
                             self.decrypted_manifest_filename)
            )
            self._converter = _IosManifest(self.manifest)
        else:
            self._settings.set_encrypted(True)
            self.manifest = None
            self._converter = None

        # Store in case re-decryption is required
        self._passphrase = None
        self._backup = None

    @classmethod
    def is_device_filesystem(cls, path):
        return (
            os.path.exists(os.path.join(path, 'Manifest.db'))
            and os.path.exists(os.path.join(path, 'Info.plist'))
            and _ios_filesystem_is_encrypted(path)
        )

    @classmethod
    def create(cls, id_: str, root: str) -> 'DeviceFilesystem':
        if os.path.exists(root):
            raise FileExistsError(root)

        os.makedirs(root)

        # Create Manifest for file hashing. Do this manually because we don't have a device yet.
        syspath = os.path.join(root, 'Manifest.db')

        with sqlite3_connect_with_regex_support(syspath) as conn:
            conn.execute("""CREATE TABLE Files (
                fileID TEXT PRIMARY KEY,
                domain TEXT,
                relativePath TEXT,
                flags INTEGER,
                file BLOB)
            """)
            conn.execute('CREATE TABLE Properties (key TEXT PRIMARY KEY, value BLOB)')

        # Create Info.plist.
        with open(os.path.join(root, 'Info.plist'), 'wb'):
            pass  # touch the file to ensure it exists

        obj = cls(id_, root)
        obj._settings.set_subset_fs(True)
        return obj

    def is_subset_filesystem(self) -> bool:
        return self._settings.is_subset_fs()

    def scandir(self, path) -> list[str]:
        return []

    def listdir(self, path) -> list[str]:
        query = Query.from_(self.file_table).select('fileID', 'relativePath')
        query = query.where(self.file_table.relativePath == os.path.join(self.root, path))
        fields = get_field_indices(query)
        return [row[fields['relativePath']] for row in self.manifest.execute(str(query))]

    def exists(self, path) -> bool:
        # If there is no _converter then there is no "Manifest-decrypted.db"
        # so return False to avoid crashing RIME.
        if self._converter:
            real_path = self._converter.get_hashed_pathname(path)
            return os.path.exists(os.path.join(self.root, real_path))
        else:
            return False

    def getsize(self, path) -> int:
        return os.path.getsize(os.path.join(self.root, self._converter.get_hashed_pathname(path)))

    def open(self, path):
        # TODO: Should cope with blobs in the manifest too
        return open(os.path.join(self.root, self._converter.get_hashed_pathname(path), 'rb'))

    def create_file(self, path):
        raise NotImplementedError

    def sqlite3_connect(self, path, read_only=True):
        """
        Connect to a (decrypted) SQLite database for the specific path.
        """

        # If the Manifest file hasn't been decrypted yet then we cannot
        # use it to get the mapping from `domain/relativePath` to `fileID`
        if not self._converter:
            raise NotDecryptedError

        # Decrypt the file and store it with a new filename
        decrypted_hashed_pathname = self._converter.get_hashed_pathname(path) + '-decrypted'
        decrypted_file_path = os.path.join(self.root, decrypted_hashed_pathname)

        # Decrypt the file only if it's not already decrypted
        if not os.path.exists(decrypted_file_path):
            self.decrypt_file(path, decrypted_hashed_pathname)

        # Connect to the decrypted SQLite DB
        db_url = self.sqlite3_uri(decrypted_file_path, read_only)
        log.debug(f"iOS connecting to {db_url} ({path})")
        return sqlite3_connect_with_regex_support(db_url, uri=True)

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

    def is_encrypted(self) -> bool:
        return self._settings.is_encrypted()

    def set_passphrase(self, passphrase: str):
        print(f'Setting passphrase for device "{self.id_}" to "{passphrase}"')
        self._passphrase = passphrase

    def decrypt_file(self, path, decrypted_hashed_pathname):
        """
        Get the relative_path and store a decrypted file alongside the
        encrypted one.
        """

        # If there is currently not an EncryptedBackup object then we need
        # to decrypt with the `passphrase` and get the decrypted Manifest
        # and keychain that can be used to decrypt the file.
        if not self._backup:
            self._decrypt_backup()

        _, relative_path = path.split('/', 1)

        self._backup.extract_file(
            relative_path=relative_path,
            output_filename=os.path.join(self.root, decrypted_hashed_pathname)
        )

    def _decrypt_backup(self):
        """
        Based on the stored passphrase, decrypt the encrypted root directory
        Keep _backup in state to decrypt specific files if needed.
        """

        if self._passphrase:
            # TODO: change that to log.info(); usefull to know that decryption takes
            # time when the system slows down due to it
            print(f'Decrypting backup at: "{self.root}" with passphrase: "{self._passphrase}"')

            try:

                decrypted_manifest_path = os.path.join(self.root, self.decrypted_manifest_filename)

                self._backup = EncryptedBackup(backup_directory=self.root, passphrase=self._passphrase)
                self._backup.save_manifest_file(decrypted_manifest_path)

                self._settings.set_encrypted(False)

            except ValueError:
                print('Failed to decrypt. Incorrect passphrase.')
                raise WrongPassphraseError

        else:
            raise NoPassphraseError

    def decrypt(self, passphrase: str) -> bool:
        """
        Decrypt the file system and store the decrypted Manifest if it is not
        already decrypted.
        """

        self._passphrase = passphrase

        decrypted_manifest_path = os.path.join(self.root, self.decrypted_manifest_filename)

        # If the decrtyped Manifest does not exist then decrypt it; also
        # re-decrypt if one of the files is not decrtyped and we need to decrypt
        if not os.path.exists(decrypted_manifest_path):
            self._decrypt_backup()

        self.manifest = sqlite3_connect_with_regex_support(decrypted_manifest_path)
        self._converter = _IosManifest(self.manifest)

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
    def __init__(self, base_path, passphrases):
        self.base_path = base_path
        self.passphrases = passphrases
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

                        # If the FileSystem is encrypted and there is
                        # a passphrase provided as part of the YAML configuration
                        # (probably in `rime_settings.yaml`) then decrypt it
                        if (('Encrypted' in fs_cls.__name__)
                                and self.passphrases
                                and (filename in self.passphrases)):
                            filesystems[filename].decrypt(self.passphrases[filename])

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
        self.filesystems[key].lock(locked)

        return self[key]

    def is_valid_device_id(self, key):
        return VALID_DEVICE_ID_REGEX.match(key)

    def delete(self, key):
        if key not in self.filesystems:
            raise FileNotFoundError(key)

        shutil.rmtree(os.path.join(self.base_path, key))
        del self.filesystems[key]
