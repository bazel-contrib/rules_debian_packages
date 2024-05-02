"""A module extension for registering an APT package repository from a lockfile."""

load(":defs.bzl", _apt_repository = "apt_repository")

def _apt_extension_impl(module_ctx):
    for module in module_ctx.modules:
        for repository in module.tags.repository:
            _apt_repository(
                name = repository.name,
                repo_name = repository.name,
                lock_file = repository.lock_file,
                default_distro = repository.default_distro,
                default_arch = repository.default_arch,
            )

_repository_tag_class = tag_class(
    doc = "Register an APT package repository from a lockfile.",
    attrs = {
        "name": attr.string(
            doc = "A unique name for this repository.",
            mandatory = True,
        ),
        "lock_file": attr.label(
            doc = "The lockfile to generate a repository from.",
            allow_single_file = True,
            mandatory = True,
        ),
        "default_distro": attr.string(
            doc = "The distribution to assume as default.",
            mandatory = True,
        ),
        "default_arch": attr.string(
            doc = "The architecture to assume as default.",
            mandatory = True,
        ),
    },
)
apt = module_extension(
    implementation = _apt_extension_impl,
    tag_classes = { "repository": _repository_tag_class },
)
