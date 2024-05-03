import argparse
import logging
from pathlib import Path
import yaml

from apt.private.lockfile_generator.config import (
    Architecture,
    Distribution,
    PackagesConfig,
    SnapshotMap,
)
from apt.private.lockfile_generator.lockfile import generate_lockfile

logging.basicConfig(level=logging.WARNING)

logger = logging.getLogger("lockfile_generator")


def get_latest_snapshots(distros: list[Distribution]) -> SnapshotMap:
    snapshots = dict[str, str]()

    # Randomly chosen architecture, assuming snapshot timestamps are the same for
    # all architectures.
    arch = Architecture.AMD64
    for distro in set(distros):
        snapshots.update(distro.latest_snapshot(arch))

    return snapshots


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

    snapshots = yaml.safe_load(args.snapshots_file.open())
    if not isinstance(snapshots, dict):
        raise ValueError(f"Invalid snapshots file: {args.snapshots_file}")
    for value in snapshots.values():
        if not isinstance(value, str):
            raise ValueError(f"Invalid snapshots file: {args.snapshots_file}")

    packages = PackagesConfig.from_yaml_file(args.packages_file)
    if not isinstance(packages, list):
        packages = [packages]

    distros = [distro for pc in packages for distro in pc.get_distros()]

    if args.update_snapshots_file:
        logger.debug("Retrieving latest snapshots ...")
        latest_snapshots = get_latest_snapshots(distros=distros)
        if snapshots == latest_snapshots:
            logger.info("Already at latest snapshots.")
        else:
            snapshots = latest_snapshots
            logger.info(f"Using new snapshots: {snapshots}")

    logger.debug("Generating lockfile ...")
    lockfile = generate_lockfile(
        snapshots=snapshots,
        packages_config=packages,
    )

    if args.dry_run:
        logger.info("Dry run. not writing files!")
        logger.debug(lockfile.to_json())
    else:
        yaml.safe_dump(snapshots, args.snapshots_file.open("w"))
        lockfile.to_json_file(args.lock_file, indent=2, sort_keys=True)


if __name__ == "__main__":
    main()
