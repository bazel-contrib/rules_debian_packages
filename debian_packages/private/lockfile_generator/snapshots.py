import re
import logging
from datetime import date

import requests

from debian_packages.private.lockfile_generator.config import SnapshotsConfig

logger = logging.getLogger(__name__)


def _get_latest_snapshot(snapshot_name: str, mirror: str) -> str:
    logger.debug(
        f"Retrieving latest snapshot for '{snapshot_name}' from '{mirror}' ..."
    )
    response = requests.get(
        url=f"{mirror}/archive/{snapshot_name}/",
        params={
            "year": date.today().year,
            "month": date.today().month,
        },
    )
    snapshots = re.findall("[0-9]+T[0-9]+Z", response.text)
    latest_snapshot = snapshots[-1]
    logger.debug(f"Latest snapshot for '{snapshot_name}': {latest_snapshot}")
    return latest_snapshot


def get_latest_snapshots(mirror: str) -> SnapshotsConfig:
    main = _get_latest_snapshot(snapshot_name="debian", mirror=mirror)
    security = _get_latest_snapshot(snapshot_name="debian-security", mirror=mirror)
    return SnapshotsConfig(
        main=main,
        security=security,
    )
