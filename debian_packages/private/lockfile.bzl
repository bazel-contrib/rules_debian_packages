"""Implementation of the debian_packages_lockfile rule."""

load("@bazel_skylib//rules:write_file.bzl", "write_file")

def debian_packages_lockfile(
        name,
        snapshots_file = "snapshots.yaml",
        packages_file = "packages.yaml",
        lock_file = "packages.lock",
        mirror = "https://snapshot.debian.org",
        verbose = False,
        debug = False):
    """Macro that generates lockfile-generator targets.

    It creates two target to generate a lockfile and updating the snapshots.

    You can `bazel run [name].generate` to generate a lockfile containing the
    packages defined in `[packages_file]` as resolved again `[snapshots_file]`.

    You can `bazel run [name].update` to update the used snapshot and regenerate
    the lockfile.

    Args:
      name: The name of the lockfile-target.
      snapshots_file: The file to read or write the debian snapshots from.
      packages_file: The file to read the desired packages from.
      lock_file: The file to write locked packages to.
      mirror: The debian-snapshot host to use.
      verbose: Enable verbose logging.
      debug: Enable debug logging.
    """
    lockfile_generator = Label("//debian_packages/private/lockfile_generator:binary")

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
        "--mirror {}".format(mirror),
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
