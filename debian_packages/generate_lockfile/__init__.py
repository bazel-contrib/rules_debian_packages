import argparse
import logging
from pathlib import Path

from debian_packages.generate_lockfile.config import PackagesConfig, SnapshotsConfig
from debian_packages.generate_lockfile.lockfile import generate_lockfile
from debian_packages.generate_lockfile.snapshots import get_latest_snapshots

logging.basicConfig(level=logging.WARNING)

logger = logging.getLogger("debian_packages.generate_lockfile")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--snapshots-file", type=Path, required=True)
    parser.add_argument("--packages-file", type=Path, required=True)
    parser.add_argument("--lock-file", type=Path, required=True)
    parser.add_argument("--update-snapshots-file", action="store_true", default=False)
    parser.add_argument("--dry-run", action="store_true", default=False)
    parser.add_argument("--verbose", action="store_true", default=False)
    parser.add_argument("--debug", action="store_true", default=False)
    return parser.parse_args()


def main():
    args = parse_args()
    if args.verbose:
        logger.setLevel(logging.INFO)

    if args.debug:
        logger.setLevel(logging.DEBUG)

    snapshots = SnapshotsConfig.from_yaml_file(args.snapshots_file)

    if args.update_snapshots_file:
        logger.debug("Retrieving latest snapshots ...")
        latest_snapshots = get_latest_snapshots()
        if snapshots == latest_snapshots:
            logger.info("Already at latest snapshots.")
        else:
            snapshots = latest_snapshots
            logger.info(f"Using new snapshots: {snapshots}")

    packages = PackagesConfig.from_yaml_file(args.packages_file)

    logger.debug("Generating lockfile ...")
    lockfile = generate_lockfile(
        snapshots_config=snapshots,
        packages_config=packages,
    )

    if args.dry_run:
        logger.info("Dry run. not writing files!")
        logger.debug(lockfile.to_json())
    else:
        snapshots.to_yaml_file(args.snapshots_file)
        lockfile.to_json_file(args.lock_file, indent=2, sort_keys=True)
