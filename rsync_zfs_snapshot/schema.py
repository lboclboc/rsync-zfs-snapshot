#!/usr/bin/env python3
import configparser
import os


class Schema:
    known_labels = ["hourly", "daily", "weekly", "monthly", "yearly"]

    def __init__(self, config_file: str = "/tmp/rsync-zfs-snapshot.conf") -> None:
        self.config_file = config_file
        if not os.path.exists(self.config_file):
            raise RuntimeError(f"{self.config_file}: config file not found")
        self.config = configparser.ConfigParser()
        self.config.read(self.config_file)

    def get_count(self, section, label) -> int:
        if label not in Schema.known_labels:
            raise RuntimeError(f"schema section {section} does not have the label {label}")
        count = self.config.getint(section, label, fallback=None)
        if count is not None and count < 0:
            raise RuntimeError(f"count for {label} of schedule {section} is negative")
        return count

