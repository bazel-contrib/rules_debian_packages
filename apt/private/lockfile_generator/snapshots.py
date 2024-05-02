import re
import logging
from datetime import date, timedelta

import requests

from apt.private.lockfile_generator.config import SnapshotsConfig

logger = logging.getLogger(__name__)


def _get_latest_ubuntu_snapshot(release_name: str, mirror: str, arch: str) -> str:
    logger.debug(f"Retrieving latest snapshot for '{release_name}' from '{mirror}' ...")
    latest_snapshot = ""
    for x in range(0, 10):
        testdate = date.today() - timedelta(days=x)
        testtimestamp = "{0:%Y}{0:%m}{0:%d}T000000Z".format(testdate)
        url = f"{mirror}/ubuntu/{testtimestamp}/dists/{release_name}/main/binary-{arch}/Packages.xz"
        response = requests.get(url=url)
        if response.ok:
            latest_snapshot = testtimestamp
            break
    logger.debug(f"Latest snapshot for '{release_name}': {latest_snapshot}")
    return latest_snapshot


def _get_latest_debian_snapshot(mirror: str, release_name: str) -> str:
    logger.debug(f"Retrieving latest snapshot for '{release_name}' from '{mirror}' ...")
    response = requests.get(
        url=f"{mirror}/archive/{release_name}/",
        params={
            "year": date.today().year,
            "month": date.today().month,
        },
    )
    snapshots = re.findall("[0-9]+T[0-9]+Z", response.text)
    latest_snapshot = snapshots[-1]
    logger.debug(f"Latest snapshot for '{release_name}': {latest_snapshot}")
    return latest_snapshot


def get_latest_snapshots(mirror: str, release="", arch="") -> SnapshotsConfig:
    if "ubuntu" in mirror:
        main = _get_latest_ubuntu_snapshot(
            release_name=release, mirror=mirror, arch=arch
        )
        security = _get_latest_ubuntu_snapshot(
            release_name=release, mirror=mirror, arch=arch
        )
    else:
        release = "debian"
        main = _get_latest_debian_snapshot(release_name=release, mirror=mirror)
        security = _get_latest_debian_snapshot(
            release_name=release + "-security", mirror=mirror
        )
    return SnapshotsConfig(
        main=main,
        security=security,
    )
