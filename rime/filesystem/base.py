# This software is released under the terms of the GNU GENERAL PUBLIC LICENSE.
# See LICENSE.txt for full details.
# Copyright 2023 Telemarq Ltd

from dataclasses import dataclass
import os
import stat
from typing import Optional


@dataclass(frozen=True, unsafe_hash=True)
class File:
    """
    """
    pathname: str
    mime_type: Optional[str] = None


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
