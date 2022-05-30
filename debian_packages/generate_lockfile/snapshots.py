import re
import logging
from datetime import date

import requests

from debian_packages.generate_lockfile.config import SnapshotsConfig

logger = logging.getLogger(__name__)


def _get_latest_snapshot(snapshot_name: str) -> str:
    logger.debug(f"Retrieving latest snapshot for '{snapshot_name}' ...")
    response = requests.get(
        url=f"https://snapshot.debian.org/archive/{snapshot_name}/",
        params={
            "year": date.today().year,
            "month": date.today().month,
        },
    )
    snapshots = re.findall("[0-9]+T[0-9]+Z", response.text)
    latest_snapshot = snapshots[-1]
    logger.debug(f"Latest snapshot for '{snapshot_name}': {latest_snapshot}")
    return latest_snapshot


def get_latest_snapshots() -> SnapshotsConfig:
    main = _get_latest_snapshot("debian")
    security = _get_latest_snapshot("debian-security")
    return SnapshotsConfig(
        main=main,
        security=security,
    )
