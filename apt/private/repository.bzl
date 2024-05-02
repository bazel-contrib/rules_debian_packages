"""Implementation of the apt_repository rule."""

load("utils.bzl", "package_name")

_doc = """A repository rule to download .deb packages using Bazel's downloader.

Typical usage in `WORKSPACE.bazel`:

```starlark
load("@rules_apt//apt:defs.bzl", "apt_repository")

apt_repository(
    name = "my_debian_packages",
    default_arch = "amd64",
    default_distro = "debian12",
    lock_file = "//path/to:debian_packages.lock",
)

load("@my_debian_packages//:packages.bzl", "install_deps")

install_deps()
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

    layer_build_template = rctx.read(
        rctx.path(
            Label("@rules_apt//apt/private:LAYER_BUILD.template.bazel"),
        ),
    )

    files = []
    for distro, archs in lock_file_files.items():
        for arch, arch_files in archs.items():
            for file in arch_files:
                filename = file["url"].split("/")[-1]
                deb_folder = package_name(file["name"], distro, arch)

                # For debfile
                rctx.download(
                    url = [file["url"]],
                    sha256 = file["sha256"],
                    output = filename,
                )

                # For debfile_layer
                rctx.extract(
                    archive = filename,
                    output = deb_folder,
                )

                rctx.file(
                    deb_folder + "/BUILD.bazel",
                    layer_build_template,
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
        Label("@rules_apt//apt/private:REPO_BUILD.template.bazel"),
        substitutions = {
            "{REPOSITORY}": rctx.attr.repo_name,
            "{PACKAGES}": str(tuple(packages)),
        },
    )

    rctx.template(
        "packages.bzl",
        Label("@rules_apt//apt/private:packages.template.bzl"),
        substitutions = {
            "{REPOSITORY}": rctx.attr.repo_name,
            "{DEFAULT_DISTRO}": rctx.attr.default_distro,
            "{DEFAULT_ARCH}": rctx.attr.default_arch,
            "{FILES}": str(tuple(files)),
        },
    )

_attrs = {
    "repo_name": attr.string(
        doc = "Name of the repository. Required because Bzlmod canonicalizes the repository name.",
        mandatory = True,
    ),
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

apt_repository = repository_rule(
    implementation = _impl,
    attrs = _attrs,
    doc = _doc,
)
