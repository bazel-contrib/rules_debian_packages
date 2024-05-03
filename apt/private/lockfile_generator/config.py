import abc
from dataclasses import dataclass, field
from datetime import date, timedelta
from enum import Enum
import logging
import re
from typing import TYPE_CHECKING, ClassVar, TypeAlias
from typing_extensions import override

from dataclass_wizard import JSONSerializable, JSONFileWizard, YAMLWizard
import requests

if TYPE_CHECKING:
    from apt.private.lockfile_generator.package_index import PackageIndex

logger = logging.getLogger(__name__)


SnapshotMap: TypeAlias = dict[str, str]


class Architecture(str, Enum):
    AMD64 = "amd64"
    ARM64 = "arm64"
    ARM = "arm"
    PPC64LE = "ppc64le"
    S390X = "s390x"

    def __str__(self) -> str:
        return self.value


class Channel(str, Enum):
    MAIN = "main"
    UPDATES = "updates"
    SECURITY = "security"


class Distribution(abc.ABC):
    """Base class for distributions, which determines the deb repository URL."""

    KIND: ClassVar[str]

    codename: str

    def __init__(self, codename: str):
        """
        Initialize the distribution.

        Args:
            mirror: The mirror URL for the distribution.
            codename: The codename for this release. This should be the name
                represented in the APT repository URL.
        """

        self.codename = codename

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(codename={self.codename!r})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Distribution):
            return NotImplemented

        return self.KIND == other.KIND and self.codename == other.codename

    def __hash__(self) -> int:
        return hash((self.KIND, self.codename))

    @property
    @abc.abstractmethod
    def repositories(self) -> list[str]:
        """Get the repositories for the distribution."""

    def package_indexes(
        self, arch: Architecture, snapshots: SnapshotMap
    ) -> list["PackageIndex"]:
        """
        Get the package indexes for the distribution.

        Args:
            arch: The system architecture.
            snapshots: The snapshot mapping for each repository.
        """
        from apt.private.lockfile_generator.package_index import PackageIndex

        return [
            PackageIndex(
                distro=self,
                arch=arch,
                repository=repository,
                channel=channel,
                snapshot=snapshots[f"{self.KIND}-{self.codename}-{channel.value}"],
            )
            for repository in self.repositories
            for channel in Channel
        ]

    @abc.abstractmethod
    def pool_root_url(self, channel: Channel, snapshot: str) -> str:
        """
        Get the root URL for the APT repository's pool directory.

        Args:
            channel: The distribution channel.
            snapshot: The snapshot version.
        """

    @abc.abstractmethod
    def packages_url(
        self, repository: str, channel: Channel, arch: Architecture, snapshot: str
    ) -> str:
        """
        Get the URL for the Packages.xz file.

        Args:
            repository: The distribution channel.
            channel: The distribution channel.
            arch: The system architecture.
            snapshot: The snapshot version.
        """

    @abc.abstractmethod
    def latest_snapshot(self, arch: Architecture) -> SnapshotMap:
        """
        Get the latest snapshot for the distribution.

        Args:
            arch: The system architecture.

        Returns:
            A mapping of "KIND-CODENAME-CHANNEL" to the snapshot version.
        """


class Debian(Distribution):
    KIND = "debian"
    MIRROR = "https://snapshot.debian.org"
    OLD_SECURITY_CODENAMES = {"jessie", "stretch", "buster"}

    def __init__(self, codename: str):
        self.codename = codename

    @property
    @override
    def repositories(self) -> list[str]:
        return ["main", "contrib", "non-free"]

    @override
    def pool_root_url(self, channel: Channel, snapshot: str) -> str:
        match channel:
            case (Channel.MAIN, Channel.UPDATES):
                return f"{self.MIRROR}/archive/debian/{snapshot}"
            case Channel.SECURITY:
                return f"{self.MIRROR}/archive/debian-security/{snapshot}"
            case _:
                raise ValueError(f"Invalid channel: {channel}")

    @override
    def packages_url(
        self, repository: str, channel: Channel, arch: Architecture, snapshot: str
    ) -> str:
        codename = self.codename
        if channel == Channel.UPDATES:
            codename += "-updates"
        elif channel == Channel.SECURITY:
            if codename in self.OLD_SECURITY_CODENAMES:
                codename += "/updates"
            else:
                codename += "-security"

        return f"{self.pool_root_url(channel, snapshot)}/dists/{codename}/{repository}/binary-{arch}/Packages.xz"

    def _latest_channel_snapshot(self, channel: str) -> str:
        response = requests.get(
            url=f"{self.MIRROR}/archive/{channel}/",
            params={
                "year": date.today().year,
                "month": date.today().month,
            },
        )
        snapshot = re.search("[0-9]+T[0-9]+Z", response.text)
        if not snapshot:
            raise ValueError(f"Failed to find snapshot for {channel}")
        return snapshot.group()

    @override
    def latest_snapshot(self, arch: Architecture) -> SnapshotMap:
        logger.debug(f"Retrieving latest snapshot for Debian from '{self.MIRROR}'...")

        snapshots = dict[str, str]()
        for channel, debian_channel in (
            (Channel.MAIN, "debian"),
            (Channel.SECURITY, "debian-security"),
        ):
            snapshot = self._latest_channel_snapshot(debian_channel)
            logger.debug(f"Latest snapshot for '{channel}': {snapshot}")
            snapshots[channel.value] = snapshot

        # updates is the same as main
        snapshots[Channel.UPDATES.value] = snapshots[Channel.MAIN.value]

        return {
            f"{self.KIND}-{self.codename}-{channel}": snapshot
            for channel, snapshot in snapshots.items()
        }


class Ubuntu(Distribution):
    KIND = "ubuntu"
    MIRROR = "https://snapshot.ubuntu.com"

    def __init__(self, codename: str):
        self.codename = codename

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.codename!r})"

    @property
    @override
    def repositories(self) -> list[str]:
        return ["main", "restricted", "universe", "multiverse"]

    @override
    def pool_root_url(self, channel: Channel, snapshot: str) -> str:
        return f"{self.MIRROR}/ubuntu/{snapshot}"

    @override
    def packages_url(
        self, repository: str, channel: Channel, arch: Architecture, snapshot: str
    ) -> str:
        codename = self.codename
        if channel == Channel.UPDATES:
            codename += "-updates"
        elif channel == Channel.SECURITY:
            codename += "-security"

        return f"{self.pool_root_url(channel, snapshot)}/dists/{codename}/{repository}/binary-{arch}/Packages.xz"

    @override
    def latest_snapshot(self, arch: Architecture) -> SnapshotMap:
        logger.debug(
            f"Retrieving latest snapshot for Ubuntu {self.codename} from '{self.MIRROR}'..."
        )

        latest_snapshot: str | None = None
        for x in range(0, 10):
            testdate = date.today() - timedelta(days=x)
            testtimestamp = "{0:%Y}{0:%m}{0:%d}T000000Z".format(testdate)
            response = requests.get(
                url=self.packages_url("main", Channel.MAIN, arch, testtimestamp)
            )
            if response.ok:
                latest_snapshot = testtimestamp
                break
        else:
            raise ValueError(f"Failed to find snapshot for Ubuntu {self.codename}")

        logger.debug(f"Latest snapshot for '{self.codename}': {latest_snapshot}")
        return {
            f"{self.KIND}-{self.codename}-{channel.value}": latest_snapshot
            for channel in Channel
        }


class Distributions(Enum):
    DEBIAN8 = Debian("jessie")
    DEBIAN9 = Debian("stretch")
    DEBIAN10 = Debian("buster")
    DEBIAN11 = Debian("bullseye")
    DEBIAN12 = Debian("bookworm")
    DEBIAN13 = Debian("trixie")

    UBUNTU1404 = Ubuntu("trusty")
    UBUNTU1604 = Ubuntu("xenial")
    UBUNTU1804 = Ubuntu("bionic")
    UBUNTU2004 = Ubuntu("focal")
    UBUNTU2204 = Ubuntu("jammy")
    UBUNTU2404 = Ubuntu("noble")

    def __str__(self) -> str:
        return str(self.value)


CODENAME_TO_DISTRIBUTION = {
    # Debian version number
    "debian8": Distributions.DEBIAN8,
    "debian9": Distributions.DEBIAN9,
    "debian10": Distributions.DEBIAN10,
    "debian11": Distributions.DEBIAN11,
    "debian12": Distributions.DEBIAN12,
    "debian13": Distributions.DEBIAN13,
    # Debian codename
    "jessie": Distributions.DEBIAN8,
    "stretch": Distributions.DEBIAN9,
    "buster": Distributions.DEBIAN10,
    "bullseye": Distributions.DEBIAN11,
    "bookworm": Distributions.DEBIAN12,
    "trixie": Distributions.DEBIAN13,
    # Ubuntu version number
    "ubuntu1404": Distributions.UBUNTU1404,
    "ubuntu1604": Distributions.UBUNTU1604,
    "ubuntu1804": Distributions.UBUNTU1804,
    "ubuntu2004": Distributions.UBUNTU2004,
    "ubuntu2204": Distributions.UBUNTU2204,
    "ubuntu2404": Distributions.UBUNTU2404,
    # Ubuntu codename
    "trusty": Distributions.UBUNTU1404,
    "xenial": Distributions.UBUNTU1604,
    "bionic": Distributions.UBUNTU1804,
    "focal": Distributions.UBUNTU2004,
    "jammy": Distributions.UBUNTU2204,
    "noble": Distributions.UBUNTU2404,
}


@dataclass
class PackagesConfig(YAMLWizard):
    architectures: list[Architecture]
    distros: list[str]
    packages: list[str]
    exclude_packages: list[str] = field(default_factory=list)
    package_priorities: list[list[str]] = field(default_factory=list)

    def get_distros(self) -> list[Distribution]:
        return [CODENAME_TO_DISTRIBUTION[d].value for d in self.distros]


@dataclass
class Package:
    name: str
    dependencies: list[str]


@dataclass
class Debfile:
    name: str
    version: str | None
    url: str
    sha256: str


@dataclass
class Lockfile(JSONSerializable, JSONFileWizard):
    snapshots: SnapshotMap
    packages: dict[str, dict[Architecture, list[Package]]]
    files: dict[str, dict[Architecture, list[Debfile]]]
