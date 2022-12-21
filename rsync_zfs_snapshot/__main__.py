import argparse
import logging
import os
from rsync_zfs_snapshot.rsync_zfs_snapshot import RsyncZFSnapshot
from rsync_zfs_snapshot.zfsapi import ZFSAPI
from rsync_zfs_snapshot.schema import Schema

RSYNC_MODULE_PATH = os.getenv("RSYNC_MODULE_PATH")
RSYNC_EXIT_STATUS = os.getenv("RSYNC_EXIT_STATUS")


def parse_arguments():
    parser = argparse.ArgumentParser(description="rsync zfs snapshot handler")
    parser.add_argument("-d", "--debug", default=False, action="store_true", help="turn on debugging")
    parser.add_argument("--schema", default="/etc/rsync-zfs-snapshot/schema.conf", help="schema database")
    parser.add_argument("schema_name", nargs=1, type=str, help="name of schema in schema database to use for snapshot")
    return parser.parse_args()

def main():
    if not RSYNC_MODULE_PATH:
        raise RuntimeError(f"This script should only be started by rsync daemon")

    args = parse_arguments()
    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
    zfsapi = ZFSAPI()

    filesystem = zfsapi.get_filesystem_for_path(RSYNC_MODULE_PATH)
    if not filesystem:
        raise RuntimeError(f"Not a zfs mount: {RSYNC_MODULE_PATH}")

    schema = Schema(args.schema)

    snapshoter = RsyncZFSnapshot(zfsapi=zfsapi, schema=schema)

    snapshoter.manage_snapshots(filesystem, args.schema_name[0])

    if RSYNC_EXIT_STATUS != "0":
        logging.error(f"The rsync process exited with error (status {RSYNC_EXIT_STATUS})")


if __name__ == "__main__":
    main()