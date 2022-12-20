from rsync_zfs_snapshot.schema import Schema
import subprocess
import unittest
from rsync_zfs_snapshot.zfsapi import ZFSAPI

RPOOL = "tank"
TESTVOL1 = f"{RPOOL}/pytest-zvol-1"
TESTVOL2 = f"{RPOOL}/pytest-zvol-2"

class TestSchema(unittest.TestCase):

    def setUp(self) -> None:
        super().setUp()
        subprocess.run(["sudo", "zfs", "create", f"{TESTVOL1}"], check=True)
        subprocess.run(["sudo", "zfs", "create", f"{TESTVOL2}"], check=True)
        subprocess.run(["sudo", "zfs", "snapshot", f"{TESTVOL2}@dummy"], check=True)  # Needed for full testing coverage.
        self.zfsapi = ZFSAPI()

    def tearDown(self) -> None:
        super().tearDown()
        subprocess.run(["sudo", "zfs", "destroy", "-r", f"{TESTVOL1}"], check=True)
        subprocess.run(["sudo", "zfs", "destroy", "-r", f"{TESTVOL2}"], check=True)

    def test_snapshots(self):
        snap1 = "xdaily-2022-10-20-1200"
        snap2 = "xdaily-2022-10-20-0900"
        snapshots = self.zfsapi.list_filesystem_snapshots(TESTVOL1)
        self.assertListEqual(snapshots, [])

        self.zfsapi.create_filesystem_snapshot(TESTVOL1, snap1)
        snapshots = self.zfsapi.list_filesystem_snapshots(TESTVOL1)
        self.assertListEqual(snapshots, [snap1])

        self.zfsapi.create_filesystem_snapshot(TESTVOL1, snap2)

        snapshots = self.zfsapi.list_filesystem_snapshots(TESTVOL1)
        self.assertListEqual(snapshots, sorted([snap1, snap2]))

    def test_volume_path(self):
        vol = self.zfsapi.get_filesystem_for_path("/" + TESTVOL1)
        self.assertEqual(vol, TESTVOL1)

        vol = self.zfsapi.get_filesystem_for_path("/no-such-path")
        self.assertEqual(vol, None)

        vol = self.zfsapi.get_filesystem_for_path("/tmp")
        self.assertEqual(vol, None)

    def test_destroy_snapshot(self):
        snap = "xweekly-2022-03"
        self.zfsapi.create_filesystem_snapshot(TESTVOL1, snap)
        self.zfsapi.destroy_filesystem_snapshot(TESTVOL1, snap)
        snapshots = self.zfsapi.list_filesystem_snapshots(TESTVOL1)
        self.assertListEqual(snapshots, [])



