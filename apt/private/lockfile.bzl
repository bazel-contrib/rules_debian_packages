"""Implementation of the apt_lockfile rule."""

load("@bazel_skylib//rules:write_file.bzl", "write_file")

def apt_lockfile(
        name,
        snapshots_file = "snapshots.yaml",
        packages_file = "packages.yaml",
        lock_file = "packages.lock",
        verbose = False,
        debug = False):
    """Macro that produces targets to interact with a lockfile.

    Produces a target `[name].generate`, which generates a lockfile containing
    packages defined in `[packages_file]` resolved against `[snapshots_file]`.

    Produces a target `[name].update`, which updates the snapshots and generates
    the lockfile.


    Typical usage in `BUILD.bazel`:

    ```starlark
    load("@rules_apt//apt:defs.bzl", "apt_lockfile")

    # Generate lockfile with:
    # bazel run //path/to:apt.generate
    # Update snapshots with:
    # bazel run //path/to:apt.update
    apt_lockfile(
        name = "apt",
        lock_file = "debian_packages.lock",
        packages_file = "debian_packages.yaml",
        snapshots_file = "debian_snapshots.yaml",
    )
    ```


    Args:
      name: The name of the lockfile-target.
      snapshots_file: The file to read or write the debian snapshots from.
      packages_file: The file to read the desired packages from.
      lock_file: The file to write locked packages to.
      verbose: Enable verbose logging.
      debug: Enable debug logging.
    """
    lockfile_generator = Label("//apt/private/lockfile_generator:binary")

    data = [
        lockfile_generator,
        snapshots_file,
        packages_file,
        lock_file,
    ]

    args = [
        "$(location {})".format(lockfile_generator),
        "--snapshots-file $(rootpath {})".format(snapshots_file),
        "--packages-file $(rootpath {})".format(packages_file),
        "--lock-file $(rootpath {})".format(lock_file),
    ]

    if verbose:
        args.append("--verbose")

    if debug:
        args.append("--debug")

    write_file(
        name = name + "_runner",
        out = name + ".runner.sh",
        content = ["$@"],
    )

    native.sh_binary(
        name = name + ".generate",
        srcs = [name + ".runner.sh"],
        data = data,
        args = args,
    )

    native.sh_binary(
        name = name + ".update",
        srcs = [name + ".runner.sh"],
        data = data,
        args = args + ["--update-snapshots-file"],
    )
