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
    DEBIAN8 = "debian8"
    DEBIAN9 = "debian9"
    DEBIAN10 = "debian10"
    DEBIAN11 = "debian11"

    def __str__(self) -> str:
        return self.value


@dataclass
class PackagesConfig(YAMLWizard):
    archs: list[Arch]
    distros: list[Distro]
    packages: list[str]
    exclude_packages: list[str] = field(default_factory=list)
    package_priorities: list[list[str]] = field(default_factory=list)


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
    debfiles: dict[Distro, dict[Arch, list[Debfile]]]
