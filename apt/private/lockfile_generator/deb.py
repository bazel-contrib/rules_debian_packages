from __future__ import annotations
import logging
import lzma
from dataclasses import dataclass, field
from typing import Optional, Union

import requests
import networkx
from debian import deb822, debian_support

from apt.private.lockfile_generator.config import (
    Arch,
    Distro,
    SnapshotsConfig,
)

logger = logging.getLogger(__name__)


def get_debian_arch(arch: Arch) -> str:
    if arch == Arch.AMD64:
        return "amd64"
    elif arch == Arch.ARM64:
        return "arm64"
    elif arch == Arch.ARM:
        return "armhf"
    elif arch == Arch.PPC64LE:
        return "ppc64el"
    elif arch == Arch.S390X:
        return "s390x"
    else:
        raise Exception(f"Unknown Architecture: {arch}")


def get_debian_distro(distro: Distro) -> str:
    # WARNING: Also edit 'config.py' to add supported distros to the enum.
    distro_map = {
        # Debian distributions
        Distro.DEBIAN8: "jessie",
        Distro.DEBIAN9: "stretch",
        Distro.DEBIAN10: "buster",
        Distro.DEBIAN11: "bullseye",
        Distro.DEBIAN12: "bookworm",
        Distro.DEBIAN13: "trixie",
        # Ubuntu distributions
        Distro.UBUNTU1404: "trusty",
        Distro.UBUNTU1604: "xenial",
        Distro.UBUNTU1804: "bionic",
        Distro.UBUNTU2004: "focal",
        Distro.UBUNTU2204: "jammy",
        Distro.UBUNTU2304: "lunar",
        Distro.UBUNTU2310: "mantic",
    }

    if distro in distro_map:
        return distro_map[distro]
    else:
        raise Exception(f"Unknown Distro: {distro}")


class PackageNotFound(Exception):
    def __init__(self, package_name: str, message: Optional[str] = None):
        if message is None:
            message = f"Package '{package_name}' not found"
        self.package_name = package_name
        super().__init__(message)


class DependencyNotFound(PackageNotFound):
    def __init__(self, package_name: str, dependency_of: str):
        self.dependency_of = dependency_of
        super().__init__(
            package_name=package_name,
            message=f"Package '{package_name}' not found (dependency of '{dependency_of}')",
        )


@dataclass
class Package:
    name: str
    version: str
    url: str
    sha256: str
    dependencies: frozenset[Union[str, frozenset[str]]] = field(
        default_factory=frozenset, repr=False
    )

    def __str__(self) -> str:
        return f"<{self.__class__.__name__} name={self.name} version={self.version}>"

    @staticmethod
    def from_deb822(
        pool_root_url: str, package: deb822.Package
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
            url=pool_root_url + package["Filename"],
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


@dataclass
class PackageIndex:
    name: str
    snapshot: str
    arch: Arch
    distro: Distro
    pool_root_url: str
    index_file_path: str
    _packages: list[Package] = field(init=False, default_factory=list)

    @property
    def index_file_url(self) -> str:
        return self.pool_root_url + self.index_file_path

    def __post_init__(self) -> None:
        logger.debug(f"{self}: fetching index file ...")
        response = requests.get(url=self.index_file_url, stream=True)
        logger.debug(f"{self}: loading index file ...")
        with lzma.open(response.raw) as f:
            for p in deb822.Packages.iter_paragraphs(f, use_apt_pkg=False):
                package = Package.from_deb822(self.pool_root_url, p)
                if isinstance(package, Package):
                    self._packages.append(package)
                else:
                    self._packages.extend(package)
        logger.debug(f"{self}: loading index file ... done")

    def __str__(self) -> str:
        return f"<{self.__class__.__name__} name={self.name} distro={self.distro!s} arch={self.arch!s} snapshot={self.snapshot!s}>"


@dataclass
class PackageIndexGroup:
    snapshots: SnapshotsConfig
    arch: Arch
    distro: Distro
    mirror: str
    main: PackageIndex = field(init=False)
    updates: PackageIndex = field(init=False)
    security: PackageIndex = field(init=False)
    _packages: networkx.DiGraph = field(init=False, default_factory=networkx.DiGraph)

    def __post_init__(self):
        self.main = self._main_package_index()
        self.updates = self._updates_package_index()
        self.security = self._security_package_index()
        self._initialize_graph()

    def _initialize_graph(self) -> None:
        packages = {}
        for index in self.main, self.updates, self.security:
            for package in index._packages:
                if package.name in packages:
                    previous_package = packages[package.name]
                    if (
                        debian_support.version_compare(
                            previous_package.version, package.version
                        )
                        != -1
                    ):
                        # previous_package is at least as recenv as package
                        continue
                packages[package.name] = package

        for package in packages.values():
            self._packages.add_node(package.name, package=package)
            for d in package.dependencies:
                if isinstance(d, frozenset):
                    for a in d:
                        self._packages.add_edge(package.name, a, alternatives=d)
                else:
                    self._packages.add_edge(package.name, d)

    def _get_package(self, package_name: str) -> Package:
        try:
            return self._packages.nodes[package_name]["package"]
        except KeyError:
            raise PackageNotFound(package_name)

    def _has_package(self, package_name: str) -> bool:
        return (package_name in self._packages.nodes) and (
            "package" in self._packages.nodes[package_name]
        )

    @property
    def debian_arch(self) -> str:
        return get_debian_arch(self.arch)

    @property
    def debian_distro(self) -> str:
        return get_debian_distro(self.distro)

    def _pool_root_url(self, snapshot) -> str:
        mirror = self.mirror
        if "ubuntu" in mirror:
            return f"{mirror}/ubuntu/{snapshot}/"
        else:
            return f"{mirror}/archive/debian/{snapshot}/"

    def _main_package_index(self) -> PackageIndex:
        snapshot = self.snapshots.main
        return PackageIndex(
            name="main",
            snapshot=snapshot,
            arch=self.arch,
            distro=self.distro,
            pool_root_url=self._pool_root_url(snapshot),
            index_file_path=f"dists/{self.debian_distro}/main/binary-{self.debian_arch}/Packages.xz",
        )

    def _updates_package_index(self) -> PackageIndex:
        snapshot = self.snapshots.main
        return PackageIndex(
            name="updates",
            snapshot=snapshot,
            arch=self.arch,
            distro=self.distro,
            pool_root_url=self._pool_root_url(snapshot),
            index_file_path=f"dists/{self.debian_distro}-updates/main/binary-{self.debian_arch}/Packages.xz",
        )

    def _security_package_index(self) -> PackageIndex:
        if "ubuntu" in self.mirror:
            return self._security_package_index_ubuntu()
        else:
            return self._security_package_index_debian()

    def _security_package_index_debian(self) -> PackageIndex:
        snapshot = self.snapshots.security
        index_file_path = f"dists/{self.debian_distro}"
        # NOTE the url changed after debian10
        if self.distro in (Distro.DEBIAN8, Distro.DEBIAN9, Distro.DEBIAN10):
            index_file_path += "/updates"
        else:
            index_file_path += "-security"
        index_file_path += f"/main/binary-{self.debian_arch}/Packages.xz"
        return PackageIndex(
            name="security",
            snapshot=snapshot,
            arch=self.arch,
            distro=self.distro,
            pool_root_url=f"{self.mirror}/archive/debian-security/{snapshot}/",
            index_file_path=index_file_path,
        )

    def _security_package_index_ubuntu(self) -> PackageIndex:
        snapshot = self.snapshots.security
        return PackageIndex(
            name="security",
            snapshot=snapshot,
            arch=self.arch,
            distro=self.distro,
            pool_root_url=self._pool_root_url(snapshot),
            index_file_path=f"dists/{self.debian_distro}-security/main/binary-{self.debian_arch}/Packages.xz",
        )

    def resolve_package(
        self,
        package_name: str,
        exclude_packages: list[str],
        package_priorities: list[list[str]],
    ) -> tuple[Package, tuple[Package]]:
        def get_dependency_graph(package_name: str) -> networkx.DiGraph:
            descendants = networkx.descendants(self._packages, package_name)
            package_graph = self._packages.subgraph(descendants.union({package.name}))
            return package_graph.copy()

        def remove_excluded_packages(dependency_graph: networkx.DiGraph) -> None:
            for p in exclude_packages:
                if p in dependency_graph.nodes:
                    logger.debug(f"excluding package: {p}")
                    dependency_graph.remove_node(p)

        def get_package_priority(package_name) -> Optional[list[str]]:
            for p in package_priorities:
                if package_name in p:
                    return p

        def resolve_package_priorities(dependency_graph: networkx.DiGraph) -> None:
            scheduled_for_removal = []
            for _, v, data in dependency_graph.edges(data=True):
                alternatives = data.get("alternatives")
                if not alternatives:
                    continue
                priorities = get_package_priority(v)
                order = priorities if priorities else alternatives
                best_match_found = False
                for p in order:
                    if best_match_found:
                        logger.debug(f"scheduling removal: {p}")
                        scheduled_for_removal.append(p)
                    elif p in dependency_graph.nodes:
                        best_match_found = True
            for p in scheduled_for_removal:
                if p in dependency_graph.nodes:
                    dependency_graph.remove_node(p)

        def generate_dependencies(dependency_graph: networkx.DiGraph) -> tuple[Package]:
            dependencies = []
            for descendant in networkx.descendants(dependency_graph, package_name):
                if not self._has_package(descendant):
                    raise DependencyNotFound(
                        package_name=descendant, dependency_of=package_name
                    )
                dependencies.append(self._get_package(descendant))
                if logger.getEffectiveLevel() == logging.DEBUG:
                    p = networkx.shortest_path(
                        dependency_graph, package.name, descendant
                    )
                    logger.debug(" -> ".join(p))
            return tuple(dependencies)

        logger.debug(
            f"{self}: resolving {package_name=} ({exclude_packages=} {package_priorities=})"
        )

        package = self._get_package(package_name)
        dependency_graph = get_dependency_graph(package_name)
        remove_excluded_packages(dependency_graph)
        resolve_package_priorities(dependency_graph)
        dependencies = generate_dependencies(dependency_graph)
        return package, dependencies
