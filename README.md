# rsync-zfs-snapshot

Helper script for managing snapshots of a zfs-volume that is used for rsync backup of other servers

## Usage

This script is meant to run as part of a rsync backup setup. Typically using rsync as a daemon for speed, and then
have a trigger in rsyncd.conf to run this script, either before or after the backup, for creating snapshots of the
zfs filesystem that was backed up to. Backups can of course come from any source supporting rsync.

The script uses a config file for defining snapshot schemas, specifying how many hourly, daily, weekly, monthly and yearly backups to keep.

Run the script like:

    rsync-zfs-snapshot schema

This will require the environent variable RSYNC_MODULE_PATH to be defined.
Triggering this script from rsyncd.config with a line like

    post-xfer exec = /usr/bin/rsync-zfs-snapshot

will call the the script when a rsync transfer is finished and rsync will pass the backuped path in env. RSYNC_MODULE_PATH

## Schema file

The backup schema config file is kept in /etc/rsync-zfs-snapshot/schema.conf and should have a content like following:

[normal]
dayily = 10
monthly = 5
yearly = 2

[critical]
hourly = 4
daily = 30
monthly = 12
yearly = 3

## Notes
Make sure to use the rsync option --inplace in order to save space for snapshots. If only a small portion of a file is changed, only that delta will consume space. Instead of whole files.
