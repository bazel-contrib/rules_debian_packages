import argparse
import logging
from pathlib import Path

from apt.private.lockfile_generator.config import (
    PackagesConfig,
    SnapshotsConfig,
)
from apt.private.lockfile_generator.lockfile import generate_lockfile
from apt.private.lockfile_generator.snapshots import get_latest_snapshots
from apt.private.lockfile_generator.deb import (
    get_debian_distro,
    get_debian_arch,
)

logging.basicConfig(level=logging.WARNING)

logger = logging.getLogger("lockfile_generator")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--snapshots-file", type=Path, required=True)
    parser.add_argument("--packages-file", type=Path, required=True)
    parser.add_argument("--lock-file", type=Path, required=True)
    parser.add_argument("--update-snapshots-file", action="store_true", default=False)
    parser.add_argument("--mirror", type=str, default="https://snapshot.debian.org")
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

    logger.info(f"Using mirror: {args.mirror}")

    packages = PackagesConfig.from_yaml_file(args.packages_file)
    release_name = get_debian_distro(packages[0].get_distros()[0])
    arch_name = get_debian_arch(packages[0].get_archs()[0])

    if args.update_snapshots_file:
        logger.debug("Retrieving latest snapshots ...")
        latest_snapshots = get_latest_snapshots(
            mirror=args.mirror, release=release_name, arch=arch_name
        )
        if snapshots == latest_snapshots:
            logger.info("Already at latest snapshots.")
        else:
            snapshots = latest_snapshots
            logger.info(f"Using new snapshots: {snapshots}")

    logger.debug("Generating lockfile ...")
    lockfile = generate_lockfile(
        snapshots_config=snapshots,
        packages_config=packages,
        mirror=args.mirror,
    )

    if args.dry_run:
        logger.info("Dry run. not writing files!")
        logger.debug(lockfile.to_json())
    else:
        snapshots.to_yaml_file(args.snapshots_file)
        lockfile.to_json_file(args.lock_file, indent=2, sort_keys=True)


if __name__ == "__main__":
    main()
