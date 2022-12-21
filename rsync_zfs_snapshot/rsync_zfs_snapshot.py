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
import logging
from typing import Protocol, List
from rsync_zfs_snapshot.schema import Schema

class ZFSInterface(Protocol):
    def list_filesystem_snapshots(self, filesystem: str) -> List[str]:
        ...  # pragma: no cover
    def create_filesystem_snapshot(self, filesystem: str, snapshot: str) -> None:
        ...  # pragma: no cover
    def get_filesystem_for_path(self, path: str) -> str:
        ...  # pragma: no cover
    def destroy_filesystem_snapshot(self, filesystem, snapshot) -> None:
        ...  # pragma: no cover


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
                logging.debug(f"no {schedule} schedule for {filesystem}")
                continue

            datestring = self.timestamp.strftime(dateformat)
            snapshot_name = f"{schedule}-{datestring}"
            if snapshot_name not in all_snapshots:
                self.zfsapi.create_filesystem_snapshot(filesystem, snapshot_name)
                all_snapshots.append(snapshot_name)
                logging.debug(f"created snapshot {snapshot_name} for {filesystem}")
            else:
                logging.debug(f"snapshot {snapshot_name} already exist for {filesystem}")

            snapshots = list(filter(lambda s: s.startswith(f"{schedule}-"), all_snapshots))
            while len(snapshots) > max_count:
                for_deletetion = snapshots.pop(0)
                self.zfsapi.destroy_filesystem_snapshot(filesystem, for_deletetion)
                logging.debug(f"destroyed snapshot {for_deletetion} for {filesystem}")