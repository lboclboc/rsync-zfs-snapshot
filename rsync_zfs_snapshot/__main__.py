import argparse
import os
from rsync_zfs_snapshot.rsync_zfs_snapshot import RsyncZFSnapshot
from rsync_zfs_snapshot.zfsapi import ZFSAPI
from rsync_zfs_snapshot.schema import Schema

RSYNC_MODULE_PATH = os.getenv("RSYNC_MODULE_PATH")


def parse_arguments():
    parser = argparse.ArgumentParser(description="rsync zfs snapshot handler")
    parser.add_argument("-d", default=False, action="store_true", help="turn on debugging")
    parser.add_argument("--schema", default="/etc/rsync-zfs-snapshot/schema.conf", help="schema database")
    parser.add_argument("schema_name", nargs=1, type=str, help="name of schema in schema database to use for snapshot")
    return parser.parse_args()

def main():
    if not RSYNC_MODULE_PATH:
        raise RuntimeError(f"This script should only be started by rsync daemon")

    args = parse_arguments()
    zfsapi = ZFSAPI()

    filesystem = zfsapi.get_filesystem_for_path(RSYNC_MODULE_PATH)
    if not filesystem:
        raise RuntimeError(f"Not a zfs mount: {RSYNC_MODULE_PATH}")

    schema = Schema(args.schema)

    snapshoter = RsyncZFSnapshot(zfsapi=zfsapi, schema=schema)

    snapshoter.manage_snapshots(filesystem, args.schema_name[0])

    print(filesystem)


if __name__ == "__main__":
    main()


#RSYNC_MODULE_PATH: The path configured for the module.
#RSYNC_MODULE_NAME: The name of the module being accessed.
#RSYNC_HOST_ADDR: The accessing host's IP address.
#RSYNC_HOST_NAME: The accessing host's name.
#RSYNC_USER_NAME: The accessing user's name (empty if no user).
#RSYNC_PID: A unique number for this transfer.
#RSYNC_REQUEST: (pre-xfer only) The module/path info specified by the user.  Note that the user can specify multiple source files, so the request can be something like "mod/path1 mod/path2", etc.
#RSYNC_ARG#: (pre-xfer only) The pre-request arguments are set in these numbered values. RSYNC_ARG0 is always "rsyncd", followed by the options that were used in RSYNC_ARG1, and so on.  There will be a value  of
#     "." indicating that the options are done and the path args are beginning -- these contain similar information to RSYNC_REQUEST, but with values separated and the module name stripped off.
#RSYNC_EXIT_STATUS:  (post-xfer  only) the server side's exit value.  This will be 0 for a successful run, a positive value for an error that the server generated, or a -1 if rsync failed to exit properly.  Note
#     that an error that occurs on the client side does not currently get sent to the server side, so this is not the final exit status for the whole transfer.
#RSYNC_RAW_STATUS: (post-xfer only) the raw exit value from waitpid() .

