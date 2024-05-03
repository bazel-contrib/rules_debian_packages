from __future__ import annotations
from dataclasses import dataclass, field
import logging

from debian import deb822

logger = logging.getLogger(__name__)


@dataclass
class Package:
    name: str
    url: str
    sha256: str
    version: str | None = None
    dependencies: frozenset[str | frozenset[str]] = field(
        default_factory=frozenset, repr=False
    )

    @staticmethod
    def from_deb822(
        pool_root_url: str, package: deb822.Packages
    ) -> Package | list[Package]:
        virtual_packages = []
        dependencies = []
        relations = package.relations["depends"] + package.relations["pre-depends"]
        for r in relations:
            if len(r) == 1:
                dependencies.append(r[0]["name"])
            else:
                dependencies.append(frozenset([d["name"] for d in r]))

        _package = Package(
            name=package["Package"],
            version=package["Version"],
            url=pool_root_url + "/" + package["Filename"],
            sha256=package["SHA256"],
            dependencies=frozenset(dependencies),
        )

        provides = package.relations["provides"]
        for p in provides:
            version = p[0]["version"]
            if version and len(version) == 2:
                version = version[1]
            elif version:
                logger.warning(f"BUG dont know how to handle version '{version}'")

            virtual_package = Package(
                name=p[0]["name"],
                version=version or None,
                url=_package.url,
                sha256=_package.sha256,
            )
            virtual_packages.append(virtual_package)

        if virtual_packages:
            return [_package] + virtual_packages

        return _package
