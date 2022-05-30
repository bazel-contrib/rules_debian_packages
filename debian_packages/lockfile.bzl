load("@rules_python//python:defs.bzl", "py_binary")
load("//third_party:requirements.bzl", "requirement")

def generate_lockfile(
    name,
    extra_args = [],
    visibility = ["//visibility:private"],
    snapshots_file = "snapshots.yaml",
    packages_file = "packages.yaml",
    lockfile = "packages.lock",
):

    data = [snapshots_file, packages_file, lockfile]

    generate_lockfile = Label("//debian_packages/generate_lockfile:__main__.py")
    generate_lockfile_lib = Label("//debian_packages/generate_lockfile:lib")

    loc = "$(rootpath %s)"
    common_args = [
        "--snapshots-file",
        loc % snapshots_file,
        "--packages-file",
        loc % packages_file,
        "--lock-file",
        loc % lockfile,
    ] + extra_args

    attrs = {
        "main": generate_lockfile,
        "srcs": [generate_lockfile],
        "deps": [generate_lockfile_lib],
        "data": data,
        "visibility": visibility,
    }

    py_binary(
        name = name + ".generate",
        args = common_args,
        **attrs,
    )

    py_binary(
        name = name + ".update",
        args = common_args + ["--update-snapshots-file"],
        **attrs,
    )
