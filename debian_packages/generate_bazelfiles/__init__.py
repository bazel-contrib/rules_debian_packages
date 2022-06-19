from __future__ import annotations
import argparse
import json
import textwrap
from typing import Dict
from pathlib import Path

BUILD_FILE_TEMPLATE = """\
    # AUTO GENERATED
    package(default_visibility = ["//visibility:public"])

    _PACKAGES = {packages}

    [
      filegroup(name=name, srcs=srcs)
      for name, srcs in _PACKAGES
    ]

    exports_files(["{packages_file}"])
"""

# TODO in bazel 5.2.0 http_archive supports deb-files. maybe we can use that to strip out /usr/share/{docs,man}
PACKAGES_FILE_TEMPLATE = """\
    # AUTO GENERATED
    load("@bazel_tools//tools/build_defs/repo:http.bzl", "http_file")

    _DEBFILES = {debfiles}

    def _sanitize_name(name):
        return name.replace("-", "_").replace(".", "_").replace("+", "p")

    def debian_package(name, distro = "{default_distro}", arch = "{default_arch}"):
        return "@{repo}//:" + distro + "_" + arch + "_" + _sanitize_name(name)

    def deb_file(name, distro = "{default_distro}", arch = "{default_arch}"):
        return "@{repo}_" + distro + "_" + arch + "_" + _sanitize_name(name) + "_deb//file"

    def install_deps():
        for name, url, sha256, downloaded_file_path in _DEBFILES:
            http_file(
                name = name,
                urls = [url],
                sha256 = sha256,
                downloaded_file_path = downloaded_file_path,
            )
"""


def deb_file_name(repo: str, distro: str, arch: str, name: str) -> str:
    return f"{repo}_{distro}_{arch}_{name}_deb"


def deb_file_target(repo: str, distro: str, arch: str, name: str) -> str:
    return "@" + deb_file_name(repo, distro, arch, name) + "//file"


def generate_build_file_contents(
    lock: Dict,
    repo: str,
    packages_file: Path,
) -> str:
    packages = []
    for distro, archs in lock.get("packages", {}).items():
        for arch, arch_packages in archs.items():
            for package in arch_packages:
                package_name = package["name"]
                srcs = [deb_file_target(repo, distro, arch, package_name)]
                for dep in package["dependencies"]:
                    srcs.append(deb_file_target(repo, distro, arch, dep))

                packages.append(
                    (
                        f"{distro}_{arch}_{package_name}",
                        tuple(srcs),
                    )
                )
    return textwrap.dedent(
        BUILD_FILE_TEMPLATE.format(
            repo=repo,
            packages=tuple(packages),
            packages_file=packages_file,
        )
    )


def generate_packages_file_contents(
    lock: Dict,
    repo: str,
    default_distro: str,
    default_arch: str,
) -> str:
    debfiles = []
    for distro, archs in lock.get("debfiles", {}).items():
        for arch, arch_debs in archs.items():
            for deb in arch_debs:
                package_name = deb["name"]
                debfiles.append(
                    (
                        deb_file_name(repo, distro, arch, package_name),
                        deb["url"],
                        deb["sha256"],
                        deb["url"].split("/")[-1],
                    )
                )
    return textwrap.dedent(
        PACKAGES_FILE_TEMPLATE.format(
            repo=repo,
            default_distro=default_distro,
            default_arch=default_arch,
            debfiles=tuple(debfiles),
        )
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=str, required=True)
    parser.add_argument("--default-distro", type=str, required=True)
    parser.add_argument("--default-arch", type=str, required=True)
    parser.add_argument("--lock-file", type=Path, required=True)
    parser.add_argument("--build-file", type=Path, required=True)
    parser.add_argument("--packages-file", type=Path, required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    lock = json.loads(args.lock_file.read_text())
    build_file_contents = generate_build_file_contents(
        lock=lock,
        repo=args.repo,
        packages_file=args.packages_file,
    )
    args.build_file.write_text(build_file_contents)
    packages_file_contents = generate_packages_file_contents(
        lock=lock,
        repo=args.repo,
        default_distro=args.default_distro,
        default_arch=args.default_arch,
    )
    args.packages_file.write_text(packages_file_contents)
