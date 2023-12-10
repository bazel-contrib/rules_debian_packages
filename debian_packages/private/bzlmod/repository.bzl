load("@bazel_tools//tools/build_defs/repo:http.bzl", "http_archive", "http_file")
load("@rules_debian_packages//debian_packages/private:utils.bzl", "debfile_name", "package_name")

_ARCHIVE_BUILD_FILE_CONTENT = """\
load("@rules_debian_packages//debian_packages/private:utils.bzl", "debfile_layer_rule")
debfile_layer_rule()
"""

def _debian_packages_repository_impl(rctx):
    print("IN BZLMOD REPO:", rctx.attr.name)
    lock_file_path = rctx.path(rctx.attr.lock_file)
    lock_file_content = json.decode(rctx.read(lock_file_path))
    lock_file_files = lock_file_content.get("files")
    lock_file_packages = lock_file_content.get("packages")

    for distro, archs in lock_file_files.items():
        for arch, arch_files in archs.items():
            for file in arch_files:
                http_file(
                    name = rctx.attr.name + "_" + debfile_name(file["name"], distro, arch),
                    urls = [file["url"]],
                    sha256 = file["sha256"],
                    downloaded_file_path = file["url"].split("/")[-1],
                )
                http_archive(
                    name = rctx.attr.name + "_" + package_name(file["name"], distro, arch),
                    urls = [file["url"]],
                    sha256 = file["sha256"],
                    build_file_content = _ARCHIVE_BUILD_FILE_CONTENT,
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

    print("writing BZLMOD BUILD")
    rctx.template(
        "BUILD.bazel",
        Label("@rules_debian_packages//debian_packages/private/bzlmod:repository.build.tmpl"),
        substitutions = {
            "{REPOSITORY}": rctx.attr.name,
            "{PACKAGES}": str(tuple(packages)),
        },
    )

    print("writing BZLMOD packages")
    rctx.template(
        "packages.bzl",
        Label("@rules_debian_packages//debian_packages/private/bzlmod:repository.packages.tmpl"),
        substitutions = {
            "{REPOSITORY}": rctx.attr.name,
            "{DEFAULT_DISTRO}": rctx.attr.default_distro,
            "{DEFAULT_ARCH}": rctx.attr.default_arch,
        },
    )

_debian_packages_repository_attrs = {
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
    implementation = _debian_packages_repository_impl,
    attrs = _debian_packages_repository_attrs,
)
