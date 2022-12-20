#!/usr/bin/env python3
#
# Creates zfs snapshot after sync backup.
#
# This script is intended to be run either after or before a rsync to a zfs-based backup server is done.
# The script can be invoced by pre-xfer script in /etc/rsyncd.conf or by other means.
# If the environment variable RSYNC_MODULE_PATH is provided (as done by rsync --daemon), it will
# use that zfs filesystem, otherwise the filesystem must be provided.
#

import argparse
import configparser
import datetime
import os
import subprocess

RSYNC_MODULE_PATH = os.getenv("RSYNC_MODULE_PATH")


class SnapshotSchemas:
    config_file = "/tmp/rsync-zfs-snapshot.conf"
    def __init__(self):
        if not os.path.exists(self.config_file):
            raise RuntimeError(f"{self.config_file}: config file not found")
        self.config = configparser.ConfigParser()
        config.read(self.config_file)


def get_zfs_name(dir):
    process = subprocess.run(["df", "--output=fstype,source", dir], check=False, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    if process.returncode != 0:
        return None
    lines = process.stdout.decode().split('\n')
    cols = lines[1].split()
    if cols[0] != "zfs":
        return None
    return cols[1]


def create_snapshot(zfs, schema):
    datestamp = datetime.datetime.now().strftime("%Y%m%d-%H.%M.%S")
    process = subprocess.run(["echo", "zfs", "snapshot", f"{zfs}@{datestamp}"], check=True)

def parse_arguments():
    parser = argparse.ArgumentParser(description='rsync zfs snapshot handler')
#    parser.add_argument('zfs', nargs='1', type=str, help='name of filesystem to snapshot')
    parser.add_argument('schema', nargs=1, type=str, help='name of schema to use for snapshots')
#    parser.add_argument('--log', default=sys.stdout, type=argparse.FileType('w'), help='the file where the sum should be written')
    return parser.parse_args()

def main():
    if not RSYNC_MODULE_PATH:
        raise RuntimeError(f"This script should only be started by rsync daemon")

    args = parse_arguments()

    zfs = get_zfs_name(RSYNC_MODULE_PATH)
    if not zfs:
        raise RuntimeError(f"Not a zfs mount: {RSYNC_MODULE_PATH}")

    create_snapshot(zfs, args.schema)

    print(zfs)


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

