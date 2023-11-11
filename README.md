# Bazel rules for debian_packages

A ruleset for downloading debian-packages and including them in Container Images.

**NOTE:** this ruleset is heavily inspired by [distroless](https://github.com/GoogleContainerTools/distroless)

## Features

- Pinning of the debian-snapshot to use
- Pinning of packages using a single lockfile
- Fine-grained control over packages (and their dependencies) to exclude
- Fine-grained control over package-priorities
- Compatible with [rules_docker](https://github.com/bazelbuild/rules_docker)
- Compatible with [rules_oci](https://github.com/bazel-contrib/rules_oci)

See the [examples](examples).

## Shortcomings

- There is no way to know which packages are already contained in previous layers, thus you have to be careful how you craft your package-repository.

## Installation

From the release you wish to use:
<https://github.com/betaboon/rules_debian_packages/releases>
copy the WORKSPACE snippet into your `WORKSPACE` file.

To use a commit rather than a release, you can point at any SHA of the repo.

For example to use commit `abc123`:

1. Replace `url = "https://github.com/betaboon/rules_debian_packages/releases/download/v0.1.0/rules_debian_packages-v0.1.0.tar.gz"` with a GitHub-provided source archive like `url = "https://github.com/betaboon/rules_debian_packages/archive/abc123.tar.gz"`
1. Replace `strip_prefix = "rules_debian_packages-0.1.0"` with `strip_prefix = "rules_debian_packages-abc123"`
1. Update the `sha256`. The easiest way to do this is to comment out the line, then Bazel will
   print a message with the correct value. Note that GitHub source archives don't have a strong
   guarantee on the sha256 stability, see
   <https://github.blog/2023-02-21-update-on-the-future-stability-of-source-code-archives-and-hashes/>

## Usage

Usage of this ruleset involves three main steps:

1. [Generating a lockfile](#generating-lockfile)
2. [Installing debian packages](#installing-debian-packages)
3. [Consuming debian packages](#consuming-debian-packages)

### Generating lockfile

In order to generate a lockfile, you first have to create two files: [`debian_snapshots.yaml`](#debian_snapshotsyaml) and [`debian_packages.yaml`](#debian_packagesyaml).

Then add a `BUILD` file (next to it):

```bazel
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

#### `debian_snapshots.yaml`

This file defines which snapshots to use for `main` and `security` (thus effectively pinning the versions you use)

##### Example

```yaml
main: 20220531T085056Z
security: 20220531T085321Z
```

#### `debian_packages.yaml`

This file is used to define which packages to make available in your `WORKSPACE` and finely control, among other things, dependency-resolution.

##### `distros`

This `list` defines from which debian-distros packages should be pulled.

Possible values:

- `debian8`
- `debian9`
- `debian10`
- `debian11`

**NOTE:** It is expecting distros like `debian11` instead of codenames like `bullseye` !

##### `archs`

This `list` defines for which architectures packages should be pulled.

Possible values:

- `amd64`
- `arm64`
- `arm`
- `ppc64le`
- `s390x`

##### `packages`

This `list` defines which packages to make available in your `WORKSPACE`.

##### `exclude_packages`

This `list` defines which packages (and their dependencies) to exclude while resolving dependencies.

This can be used to explicitly prevent packages from being included (e.g. "when adding git do not add perl").

##### `package_priorities`

This `list` defines which packages to prioritize over others when a package dependency states `either X or Y`.

##### Example

```yaml
- distros: ["debian11"]
  archs: ["amd64"]
  packages:
    - busybox-static
    - clinfo
    - git
  exclude_packages:
    # generally excluded from distroless
    - debconf
    - debconf-2.0
    - dpkg
    - install-info
    - debianutils
    - media-types
    - mime-support
    # prevent git from pulling in perl
    - perl
  package_priorities:
    # force clinfo to prioritize libopencl1 over ocl-icd-libopencl1
    - [libopencl1, ocl-icd-libopencl1]
```

### Installing Debian packages

To add debian packages to your `WORKSPACE`, load the `debian_repository` function and call it to create the central external repository.

```bazel
load("@rules_debian_packages//debian_packages:defs.bzl", "debian_packages_repository")

# Create a central external repo, @my_debian_packages, that contains Bazel targets for all the
# debian packages specified in the debian_packages.lock file.
debian_packages_repository(
    name = "my_debian_packages",
    default_arch = "amd64",
    default_distro = "debian11",
    lockfile = "//path/to:debian_packages.lock",
)


load("@my_debian_packages//:packages.bzl", "install_deps")

# Call the macro that defines repos for your specified debian packages.
install_deps()
```

### Consuming Debian packages

Each defined package consists of a `filegroup` that contains the package and all its dependencies.
When consuming packages in a `BUILD` file with [`container_image`](https://github.com/bazelbuild/rules_docker/blob/master/docs/container.md#container_image) you add them to `debs` by using the `debian_package()` function.

```bazel
load("@io_bazel_rules_docker//container:container.bzl", "container_image")

load("@my_debian_packages//:packages.bzl", "debian_package")

container_image(
    name = "my_container",
    base = "@cc_image_base//image",
    debs = [
        debian_package("busybox-static"),
    ],
)
```

**NOTE:** It is adviced to use `@cc_image_base//image` as the base image, as it contains the least amount of packages, thus reducing the risk of wasting space.

### Consuming DEB-files directly

You can also add the `deb` files directly, which leaves dependency-resolution up to you.

```bazel
load("@io_bazel_rules_docker//container:container.bzl", "container_image")

load("@my_debian_packages//:packages.bzl", "debfile")

container_image(
    name = "my_container",
    base = "@cc_image_base//image",
    debs = [
        debfile("busybox-static"),
    ],
)
```
