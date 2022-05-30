import logging
from collections import defaultdict
from itertools import product

from debian_packages.generate_lockfile.deb import PackageIndexGroup
from debian_packages.generate_lockfile.config import (
    Arch,
    Debfile,
    Distro,
    Lockfile,
    Package,
    PackagesConfig,
    SnapshotsConfig,
)

logger = logging.getLogger(__name__)

DistroArchTuple = tuple[Distro, Arch]


def _sanitize_name(name: str) -> str:
    return name.replace("-", "_").replace(".", "_").replace("+", "p")


def generate_lockfile(
    snapshots_config: SnapshotsConfig,
    packages_config: PackagesConfig,
) -> Lockfile:
    packages = defaultdict(lambda: defaultdict(list))
    debfiles = defaultdict(lambda: defaultdict(list))
    pigs: dict[DistroArchTuple, PackageIndexGroup] = {}
    for pc in packages_config:
        logger.debug(f"{pc=}")
        for distro, arch in product(pc.distros, pc.archs):
            logger.debug(f"{distro=} {arch=}")
            if not (distro, arch) in pigs:
                pigs[(distro, arch)] = PackageIndexGroup(
                    snapshots=snapshots_config,
                    distro=distro,
                    arch=arch,
                )
            pig = pigs[(distro, arch)]
            for package_name in pc.packages:
                logger.debug(f"resolving {package_name=!s} ...")
                package, dependencies = pig.resolve_package(
                    package_name=package_name,
                    exclude_packages=pc.exclude_packages,
                    package_priorities=pc.package_priorities,
                )
                _package = Package(
                    name=_sanitize_name(package.name),
                    dependencies=sorted([_sanitize_name(d.name) for d in dependencies]),
                )
                packages[distro][arch].append(_package)

                for d in package, *dependencies:
                    _debfile = Debfile(
                        name=_sanitize_name(d.name),
                        version=d.version,
                        url=d.url,
                        sha256=d.sha256,
                    )
                    if not _debfile in debfiles[distro][arch]:
                        debfiles[distro][arch].append(_debfile)
    for distro, arch in pigs.keys():
        packages[distro][arch].sort(key=lambda x: x.name)
        debfiles[distro][arch].sort(key=lambda x: x.name)

    return Lockfile(
        snapshots=snapshots_config,
        packages=packages,
        debfiles=debfiles,
    )
