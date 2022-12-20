from datetime import datetime
import subprocess
from typing import List
import unittest
from unittest.mock import MagicMock

from rsync_zfs_snapshot.rsync_zfs_snapshot import RsyncZFSnapshot
from rsync_zfs_snapshot.schema import Schema

RPOOL = "tank"
TESTVOL = f"{RPOOL}/pytest-zvol"

class TestZFSAPI:
    list_filesystem_snapshots = unittest.mock.NonCallableMagicMock()
    get_filesystem_for_path = unittest.mock.NonCallableMagicMock()
    create_filesystem_snapshot = unittest.mock.NonCallableMagicMock()
    destroy_filesystem_snapshot = unittest.mock.NonCallableMagicMock()


class TestRsyncZFSSnapshot(unittest.TestCase):
    def setUp(self) -> None:
        super().setUp()
        schema = Schema("tests/data/schema2.conf")
        subprocess.run(["sudo", "zfs", "create", TESTVOL], check=True)
        self.timestamp = datetime(2022, 12, 24, 15 ,0)
        self.zfsapi = TestZFSAPI()
        self.rsync_zfs_snapshot = RsyncZFSnapshot(zfsapi=self.zfsapi, schema=schema, timestamp=self.timestamp)

    def tearDown(self) -> None:
        super().tearDown()
        subprocess.run(["sudo", "zfs", "destroy", "-r", TESTVOL], check=True)

    def test_no_snapshots_exists(self):
        self.zfsapi.list_filesystem_snapshots = MagicMock(return_value=[])
        self.zfsapi.create_filesystem_snapshot = MagicMock(return_value=[])

        self.rsync_zfs_snapshot.manage_snapshots(TESTVOL, "daily2")

        self.zfsapi.list_filesystem_snapshots.assert_called_once_with(TESTVOL)
        self.zfsapi.create_filesystem_snapshot.assert_called_once_with(TESTVOL, "daily-2022-12-24")

    def test_too_many_exists(self):
        self.zfsapi.list_filesystem_snapshots = MagicMock(name="list_filsystem_snapshots", return_value=["daily-2022-12-22", "daily-2022-12-23", "daily-2022-12-24"])
        self.zfsapi.create_filesystem_snapshot = MagicMock(name="create_filsystem_snapshot", return_value=[])
        self.zfsapi.destroy_filesystem_snapshot = MagicMock(name="destroy_filsystem_snapshot", return_value=[])

        self.rsync_zfs_snapshot.manage_snapshots(TESTVOL, "daily2")

        self.zfsapi.list_filesystem_snapshots.assert_called_once_with(TESTVOL)
        self.zfsapi.create_filesystem_snapshot.assert_called_once_with(TESTVOL, "daily-2022-12-24")
        self.zfsapi.destroy_filesystem_snapshot.assert_called_once_with(TESTVOL, "daily-2022-12-22")

