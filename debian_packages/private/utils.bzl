"""Utility functions used in generated BUILD.bazel and packages.bzl"""

def sanitize_name(name):
    return name.replace("-", "_").replace(".", "_").replace("+", "p")

def debfile_name(name, distro, arch):
    return package_name(name, distro, arch) + "_debfile"

def debfile_target(repo, name, distro, arch):
    return "@" + repo + "_" + debfile_name(name, distro, arch) + "//file"

def debfile_layer_target(repo, name, distro, arch):
    return "@" + repo + "_" + package_name(name, distro, arch) + "//:layer"

def package_name(name, distro, arch):
    return sanitize_name(name) + "_" + distro + "_" + arch

def package_target(repo, name, distro, arch):
    return "@" + repo + "//:" + package_name(name, distro, arch)

def package_layer_name(name, distro, arch):
    return package_name(name, distro, arch) + "_layer"

def package_layer_target(repo, name, distro, arch):
    return "@" + repo + "//:" + package_layer_name(name, distro, arch)

def debfile_layer_rule(name = "layer"):
    native.genrule(
        name = name,
        srcs = [":data.tar.xz"],
        outs = ["data.tar"],
        cmd = "xz --decompress --stdout $< >$@",
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
