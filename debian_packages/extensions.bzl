load(":defs.bzl", "debian_packages_repository")

_repository_attrs = {
    "name": attr.string(doc = "TODO"),
    "lock_file": attr.label(),
    "default_distro": attr.string(),
    "default_arch": attr.string(),
}

def _impl(mctx):
    for mod in mctx.modules:
        for repository in mod.tags.repository:
            debian_packages_repository(
                name = repository.name,
                lock_file = repository.lock_file,
                default_distro = repository.default_distro,
                default_arch = repository.default_arch,
            )

debian_packages = module_extension(
    implementation = _impl,
    tag_classes = {
        "repository": tag_class(attrs = _repository_attrs),
    },
)
