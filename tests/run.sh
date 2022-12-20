#!/bin/bash
python3-coverage run --branch --source rsync_zfs_snapshot -m unittest discover -vvvvf tests
