import logging
import os
import subprocess
from typing import List


class ZFSAPI:
    def __init__(self):
        self.sudo = [] if os.getuid() == 0 else ["sudo"]

    def get_filesystem_for_path(self, path):
        """Return which zfs filesystem is mounted at path."""
        process = subprocess.run(["df", "--output=fstype,source", path], check=False, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        if process.returncode != 0:
            return None
        lines = process.stdout.decode().split('\n')
        cols = lines[1].split()
        if cols[0] != "zfs":
            return None
        return cols[1]

    def create_filesystem_snapshot(self, filesystem: str, snapshot:str) -> None:
        """Create snapshot for filesystem, resulting in filesystem@snapshot."""
        subprocess.run(self.sudo + ["zfs", "snapshot", f"{filesystem}@{snapshot}"], check=True)

    def list_filesystem_snapshots(self, filesystem: str) -> List[str]:
        """Return a list of snapshots for one specific filesystem."""
        process = subprocess.run(["zfs", "list", "-H", "-t", "snapshot"], stdout=subprocess.PIPE)
        snapshots = []
        for line in process.stdout.decode().split("\n"):
            # name, used, avail, refer, mount
            if not line.strip():
                continue

            cols = line.split()
            if len(cols) != 5: # pragma: no cover
                logging.warning(f"expected 5 columns from zfs list, got '{cols}'")
                continue
            v, s = cols[0].split("@")
            if v == filesystem:
                snapshots.append(s)
        return sorted(snapshots)

    def destroy_filesystem_snapshot(self, filesystem, snapshot) -> None:
        """Removes a snapshot."""
        subprocess.run(self.sudo + ["zfs", "destroy", f"{filesystem}@{snapshot}"], check=True)

