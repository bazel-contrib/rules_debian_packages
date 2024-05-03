import logging
from collections import defaultdict
from itertools import product

from apt.private.lockfile_generator.deb import PackageIndexGroup
from apt.private.lockfile_generator.config import (
    CODENAME_TO_DISTRIBUTION,
    Architecture,
    Debfile,
    Lockfile,
    Package,
    PackagesConfig,
    SnapshotMap,
)

logger = logging.getLogger(__name__)

DistroArchTuple = tuple[str, Architecture]


def _sanitize_name(name: str) -> str:
    return name.replace("-", "_").replace(".", "_").replace("+", "p")


def generate_lockfile(
    snapshots: SnapshotMap,
    packages_config: list[PackagesConfig],
) -> Lockfile:
    packages: dict[str, dict[Architecture, list[Package]]] = defaultdict(
        lambda: defaultdict(list)
    )
    files: dict[str, dict[Architecture, list[Debfile]]] = defaultdict(
        lambda: defaultdict(list)
    )
    pigs: dict[DistroArchTuple, PackageIndexGroup] = {}
    for pc in packages_config:
        logger.debug(f"{pc=}")
        for distro, arch in product(pc.distros, pc.architectures):
            logger.debug(f"{distro=} {arch=}")
            if (distro, arch) not in pigs:
                pigs[(distro, arch)] = PackageIndexGroup(
                    snapshots=snapshots,
                    distro=CODENAME_TO_DISTRIBUTION[distro].value,
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
                    _file = Debfile(
                        name=_sanitize_name(d.name),
                        version=d.version,
                        url=d.url,
                        sha256=d.sha256,
                    )
                    if not _file in files[distro][arch]:
                        files[distro][arch].append(_file)
    for distro, arch in pigs.keys():
        packages[distro][arch].sort(key=lambda x: x.name)
        files[distro][arch].sort(key=lambda x: x.name)

    return Lockfile(
        snapshots=snapshots,
        packages=packages,
        files=files,
    )
