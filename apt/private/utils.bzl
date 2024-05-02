"""Utility functions used in generated BUILD.bazel and packages.bzl"""

def sanitize_name(name):
    return name.replace("-", "_").replace(".", "_").replace("+", "p")

def debfile_name(name, distro, arch):
    return package_name(name, distro, arch) + "_debfile"

def debfile_target(repo, name, distro, arch):
    return "@" + repo + "//" + debfile_name(name, distro, arch) + ":file"

def debfile_layer_target(repo, name, distro, arch):
    return "@" + repo + "//" + package_name(name, distro, arch) + ":layer"

def package_name(name, distro, arch):
    return sanitize_name(name) + "_" + distro + "_" + arch

def package_target(repo, name, distro, arch):
    return "@" + repo + "//:" + package_name(name, distro, arch)

def package_layer_name(name, distro, arch):
    return package_name(name, distro, arch) + "_layer"

def package_layer_target(repo, name, distro, arch):
    return "@" + repo + "//:" + package_layer_name(name, distro, arch)

def debfile_layer_rule(name = "layer", srcs = ["data.tar.xz"]):
    # Some .deb archives can have non-standard data archive compression, e.g.
    # you will occasionally see `data.tar.zst`.
    #
    # This genrule handles both, so long as the input is a filegroup with a
    # single archive.
    native.genrule(
        name = name,
        srcs = srcs,
        outs = ["data.tar"],
        cmd = """
        for x in $(SRCS); do
            if [[ "$$x" = *.xz ]]; then
              xz -d --stdout "$$x" >$@
              break;
            elif [[ "$$x" = *.zst ]]; then
              zstd -f -d --stdout "$$x" >$@
              break;
            fi
        done
        """,
        visibility = ["//visibility:public"],
    )

def package_rule(repo, name, distro, arch, deps):
    srcs = []
    srcs.extend([debfile_target(repo, dep, distro, arch) for dep in deps])
    srcs.append(debfile_target(repo, name, distro, arch))
    native.filegroup(
        name = package_name(name, distro, arch),
        srcs = srcs,
    )

def package_layer_rule(repo, name, distro, arch, deps):
    srcs = []
    srcs.extend([debfile_layer_target(repo, dep, distro, arch) for dep in deps])
    srcs.append(debfile_layer_target(repo, name, distro, arch))
    native.filegroup(
        name = package_layer_name(name, distro, arch),
        srcs = srcs,
    )
