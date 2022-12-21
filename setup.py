import setuptools
import rsync_zfs_snapshot

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="rsync_zfs_snapshot",
    version=rsync_zfs_snapshot.VERSION,
    author="Lars Berntzon",
    author_email="lars.berntzon@cecilia-data.se",
    description="Snapshotting tool for use when using rsync to a zfs-based disk backup server.",
    long_description=long_description,
    long_description_content_type="text/markdown",

    url="https://github.com/psy0rz/zfs_autobackup",
    entry_points={
        'console_scripts':
            [
                'rsync-zfs-snapshot = rsync_zfs_snapshot.__main__:main',
            ]
    },
    packages=setuptools.find_packages(),

    classifiers=[
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
#    install_requires=[
#        "colorama",
#        "argparse"
#    ]
)
