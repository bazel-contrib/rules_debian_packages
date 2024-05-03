from __future__ import annotations
import logging
import lzma
from dataclasses import dataclass, field

import requests
from apt.private.lockfile_generator.config import Distribution, Architecture, Channel
from apt.private.lockfile_generator.package import Package
from debian import deb822


logger = logging.getLogger(__name__)


@dataclass
class PackageIndex:
    distro: Distribution
    arch: Architecture
    channel: Channel
    repository: str
    snapshot: str

    _packages: list[Package] | None = field(default=None, init=False, repr=False)

    @property
    def packages(self) -> list[Package]:
        """Get the packages for this index."""

        if self._packages is None:
            self._packages = self._load_packages()

        return self._packages

    def _load_packages(self) -> list[Package]:
        logger.debug(
            f"{self}: Fetching index for {self.distro} {self.channel} {self.arch} {self.snapshot}"
        )
        url = self.distro.packages_url(
            self.repository, self.channel, self.arch, self.snapshot
        )
        response = requests.get(url=url, stream=True)

        logger.debug(f"{self}: Loading index file...")
        packages = list[Package]()
        pool_root_url = self.distro.pool_root_url(self.channel, self.snapshot)
        with lzma.open(response.raw) as f:
            for paragraph in deb822.Packages.iter_paragraphs(f, use_apt_pkg=False):
                package = Package.from_deb822(pool_root_url, paragraph)
                if isinstance(package, Package):
                    packages.append(package)
                else:
                    packages.extend(package)

        logger.debug(f"{self}: Loaded {len(packages)} packages.")
        return packages
