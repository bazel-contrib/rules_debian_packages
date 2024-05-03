from __future__ import annotations
import logging
from dataclasses import dataclass, field
from typing import Optional

import networkx
from apt.private.lockfile_generator.package import Package
from debian import debian_support

from apt.private.lockfile_generator.config import (
    Architecture,
    Distribution,
    SnapshotMap,
)

logger = logging.getLogger(__name__)


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
class PackageIndexGroup:
    snapshots: SnapshotMap
    arch: Architecture
    distro: Distribution
    _packages: networkx.DiGraph = field(init=False, default_factory=networkx.DiGraph)

    def __post_init__(self):
        self._initialize_graph()

    def _initialize_graph(self) -> None:
        packages = {}

        for index in self.distro.package_indexes(self.arch, self.snapshots):
            for package in index.packages:
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
