from dataclasses import dataclass, field
from enum import Enum

from dataclass_wizard import JSONSerializable, JSONFileWizard, YAMLWizard


class Arch(Enum):
    AMD64 = "amd64"
    ARM64 = "arm64"
    ARM = "arm"
    PPC64LE = "ppc64le"
    S390X = "s390x"

    def __str__(self) -> str:
        return self.value


class Distro(Enum):
    # Be sure to also update the distro_map in
    # //debian_packages/private/lockfile_generator/deb.py

    DEBIAN8 = "debian8"
    DEBIAN9 = "debian9"
    DEBIAN10 = "debian10"
    DEBIAN11 = "debian11"
    DEBIAN12 = "debian12"
    DEBIAN13 = "debian13"

    UBUNTU1404 = "ubuntu1404"
    UBUNTU1604 = "ubuntu1604"
    UBUNTU1804 = "ubuntu1804"
    UBUNTU2004 = "ubuntu2004"
    UBUNTU2204 = "ubuntu2204"
    UBUNTU2304 = "ubuntu2304"
    UBUNTU2310 = "ubuntu2310"

    def __str__(self) -> str:
        return self.value


@dataclass
class PackagesConfig(YAMLWizard):
    archs: list[Arch]
    distros: list[Distro]
    packages: list[str]
    exclude_packages: list[str] = field(default_factory=list)
    package_priorities: list[list[str]] = field(default_factory=list)

    def get_distros(self):
        return self.distros

    def get_archs(self):
        return self.archs


@dataclass
class SnapshotsConfig(YAMLWizard):
    main: str
    security: str


@dataclass
class Package:
    name: str
    dependencies: list[str]


@dataclass
class Debfile:
    name: str
    version: str
    url: str
    sha256: str


@dataclass
class Lockfile(JSONSerializable, JSONFileWizard):
    snapshots: SnapshotsConfig
    packages: dict[Distro, dict[Arch, list[Package]]]
    files: dict[Distro, dict[Arch, list[Debfile]]]
