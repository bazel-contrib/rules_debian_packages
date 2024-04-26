"""Implementation of the debian_packages_lockfile rule."""

load("@bazel_skylib//rules:write_file.bzl", "write_file")

def debian_packages_lockfile(
        name,
        snapshots_file = "",
        packages_file = "packages.yaml",
        lock_file = "packages.lock",
        mirror = "https://snapshot.debian.org",
        exact_sources = [],
        verbose = False,
        debug = False):
    """Macro that produces targets to interact with a lockfile.

    Produces a target `[name].generate`, which generates a lockfile containing
    packages defined in `[packages_file]` resolved against `[snapshots_file]`.

    Produces a target `[name].update`, which updates the snapshots and generates
    the lockfile.


    Typical usage in `BUILD.bazel`:

    ```starlark
    load("@rules_debian_packages//debian_packages:defs.bzl", "debian_packages_lockfile")

    # Generate lockfile with:
    # bazel run //path/to:debian_packages.generate
    # Update snapshots with:
    # bazel run //path/to:debian_packages.update
    debian_packages_lockfile(
        name = "debian_packages",
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
      mirror: The debian-snapshot host to use.
      exact_sources: a list of sources from which to read. Incompatible with mirror, snapshots_file
      verbose: Enable verbose logging.
      debug: Enable debug logging.
    """
    lockfile_generator = Label("//debian_packages/private/lockfile_generator:binary")

    data = [
        lockfile_generator,
        packages_file,
        lock_file,
    ]

    if snapshots_file:
        data.append(snapshots_file)

    args = [
        "$(location {})".format(lockfile_generator),
        "--packages-file $(rootpath {})".format(packages_file),
        "--lock-file $(rootpath {})".format(lock_file),
    ]
    if exact_sources:
        args.append("--exact-sources {}".format(" ".join(exact_sources)))
    if snapshots_file:
        args.append("--snapshots-file $(rootpath {})".format(snapshots_file))
    if mirror:
        args.append("--mirror {}".format(mirror))
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
