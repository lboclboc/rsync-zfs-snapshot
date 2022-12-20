#!/usr/bin/env python3
#
# Creates zfs snapshot after sync backup.
#
# This script is intended to be run either after or before a rsync to a zfs-based backup server is done.
# The script can be invoced by pre-xfer script in /etc/rsyncd.conf or by other means.
# If the environment variable RSYNC_MODULE_PATH is provided (as done by rsync --daemon), it will
# use that zfs filesystem, otherwise the filesystem must be provided.
#
from datetime import datetime
from typing import Protocol, List
from rsync_zfs_snapshot.schema import Schema

class ZFSInterface(Protocol):
    def list_filesystem_snapshots(self, filesystem: str) -> List[str]:
        ...
    def create_filesystem_snapshot(self, filesystem: str, snapshot: str) -> None:
        ...
    def get_filesystem_for_path(self, path: str) -> str:
        ...
    def destroy_filesystem_snapshot(self, filesystem, snapshot) -> None:
        ...


class RsyncZFSnapshot:
    time_formats = {
        "hourly": "%Y-%m-%d-%H",
        "daily": "%Y-%m-%d",
        "weekly": "%Y-%U",
        "monthly": "%Y-%m",
        "yearly": "%Y",
    }

    def __init__(self, zfsapi: ZFSInterface, schema: Schema, timestamp: datetime = None):
        self.zfsapi = zfsapi
        self.schema = schema
        self.timestamp = timestamp or datetime.now()

    def manage_snapshots(self, filesystem: str, schema_name: str) -> None:
        """Manage snapshots for filesystem according to schema definitions."""
        all_snapshots = self.zfsapi.list_filesystem_snapshots(filesystem)
        for schedule, dateformat in self.time_formats.items():
            max_count = self.schema.get_count(schema_name, schedule)
            if not max_count:
                continue

            datestring = self.timestamp.strftime(dateformat)
            self.zfsapi.create_filesystem_snapshot(filesystem, f"{schedule}-{datestring}")
            snapshots = list(filter(lambda s: s.startswith(f"{schedule}-"), all_snapshots))
            while len(snapshots) > max_count:
                self.zfsapi.destroy_filesystem_snapshot(filesystem, snapshots.pop(0))
