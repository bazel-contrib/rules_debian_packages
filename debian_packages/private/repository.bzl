"""Implementation of the debian_packages_repository rule."""

_doc = """A repository rule to download debian packages using Bazel's downloader.

Typical usage in `WORKSPACE.bazel`:

```starlark
load("@rules_debian_packages//debian_packages:defs.bzl", "debian_packages_repository")

debian_packages_repository(
    name = "my_debian_packages",
    default_arch = "amd64",
    default_distro = "debian12",
    lock_file = "//path/to:debian_packages.lock",
)

load("@my_debian_packages//:packages.bzl", "install_deps")

install_deps()
```


Packages can be used for `rules_docker` based container images like this:

```starlark
load("@io_bazel_rules_docker//container:container.bzl", "container_image")
load("@my_debian_packages//:packages.bzl", "debian_package")

container_image(
    name = "my_image",
    debs = [
        debian_package("busybox-static"),
    ],
)
```


Packages can be used for `rules_oci` based container images like this:

```starlark
load("@rules_oci//oci:defs.bzl", "oci_image")
load("@my_debian_packages//:packages.bzl", "debian_package_layer")

oci_image(
    name = "my_image",
    tars = [
        debian_package_layer("busybox-static"),
    ],
)
```
"""

def _impl(rctx):
    lock_file_path = rctx.path(rctx.attr.lock_file)
    lock_file_content = json.decode(rctx.read(lock_file_path))
    lock_file_files = lock_file_content.get("files")
    lock_file_packages = lock_file_content.get("packages")

    files = []
    for distro, archs in lock_file_files.items():
        for arch, arch_files in archs.items():
            for file in arch_files:
                files.append(
                    (
                        file["name"],
                        distro,
                        arch,
                        file["url"],
                        file["sha256"],
                        file["url"].split("/")[-1],
                    ),
                )

    packages = []
    for distro, archs in lock_file_packages.items():
        for arch, arch_packages in archs.items():
            for package in arch_packages:
                packages.append(
                    (
                        package["name"],
                        distro,
                        arch,
                        tuple(package["dependencies"]),
                    ),
                )

    rctx.template(
        "BUILD.bazel",
        Label("@rules_debian_packages//debian_packages/private:repository.build.tmpl"),
        substitutions = {
            "{REPOSITORY}": rctx.attr.name,
            "{PACKAGES}": str(tuple(packages)),
        },
    )

    rctx.template(
        "packages.bzl",
        Label("@rules_debian_packages//debian_packages/private:repository.packages.tmpl"),
        substitutions = {
            "{REPOSITORY}": rctx.attr.name,
            "{DEFAULT_DISTRO}": rctx.attr.default_distro,
            "{DEFAULT_ARCH}": rctx.attr.default_arch,
            "{FILES}": str(tuple(files)),
        },
    )

_attrs = {
    "lock_file": attr.label(
        doc = "The lockfile to generate a repository from.",
        allow_single_file = True,
        mandatory = True,
    ),
    "default_distro": attr.string(
        doc = "The debian-distro to assume as default.",
        mandatory = True,
    ),
    "default_arch": attr.string(
        doc = "The architecture to assume as default.",
        mandatory = True,
    ),
}

debian_packages_repository = repository_rule(
    implementation = _impl,
    attrs = _attrs,
    doc = _doc,
)
