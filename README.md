# Bazel Debian Packages Rules

## Overview

This repository contains rules for downloading debian-packages and augmenting them into Docker Images built with [rules_docker](https://github.com/bazelbuild/rules_docker)

Currently it provides the following features:
- dependency resolution
- debian snapshots
- lockfile
- fine-grained control over packages (and their dependencies) to exclude
- fine-grained control over package-priorities
- adding individual deb-files
- adding packages and their dependencies

Current shortcomings:
- There is no way to know which packages are already contained in previous layers, thus you have to be careful how you craft your package-repository.


__NOTE:__ these rules are heavily inspired by [distroless](https://github.com/GoogleContainerTools/distroless) and [rules_python](https://github.com/bazelbuild/rules_python)

## Getting started

To import `rules_debian_packages` in your project, add the following to your `WORKSPACE` file:

```bazel
load("@bazel_tools//tools/build_defs/repo:http.bzl", "http_archive")

http_archive(
    # Get copy paste instructions for the http_archive attributes from the
    # release notes at https://github.com/betaboon/rules_debian_packages/releases
)

load("@rules_debian_packages//debian_packages:repositories.bzl", "rules_debian_packages_repositories")

rules_debian_packages_repositories()

load("@rules_debian_packages//debian_packages:deps.bzl", "rules_debian_packages_deps")

rules_debian_packages_deps()
```

## Using the packaging rules

Usage of the packaging rules involves three main steps:

1. [Generating a lockfile](#generating-lockfile)
2. [Installing debian packages](#installing-debian-packages)
3. [Consuming debian packages](#consuming-debian-packages)

The packaging rules create a central external repository that holds downloaded `deb` files and information about dependencies.
The central external repository provides a `WORKSPACE` macro to create the debian repository, as well as functions (`debian_package()` and `deb_file()`) for use in `BUILD` files.

### Generating lockfile

In order to generate a lockfile, you first have to create two files: [`debian_snapshots.yaml`](#debian_snapshotsyaml) and [`debian_packages.yaml`](#debian_packagesyaml).

Then add a `BUILD` file (next to it):

```bazel
load("@rules_debian_packages//debian_packages:lockfile.bzl", "generate_lockfile")

# Generate lockfile with:
# bazel run //path/to:debian_packages.generate
# Update snapshots with:
# bazel run //path/to:debian_packages.update
generate_lockfile(
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

__NOTE:__ It is expecting distros like `debian11` instead of codenames like `bullseye` !

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
load("@rules_debian_packages//debian_packages:repository.bzl", "debian_repository")

# Create a central external repo, @my_debian_packages, that contains Bazel targets for all the
# debian packages specified in the debian_packages.lock file.
debian_repository(
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

__NOTE:__ It is adviced to use `@cc_image_base//image` as the base image, as it contains the least amount of packages, thus reducing the risk of wasting space.

### Consuming deb-files directly

You can also add the `deb` files directly, which leaves dependency-resolution up to you.

```bazel
load("@io_bazel_rules_docker//container:container.bzl", "container_image")

load("@my_debian_packages//:packages.bzl", "deb_file")

container_image(
    name = "my_container",
    base = "@cc_image_base//image",
    debs = [
        deb_file("busybox-static"),
    ],
)
```

## API

### `debian_repository`

<pre>
debian_repository(<a href="#debian_repository-name">name</a>, <a href="#debian_repository-visibility">visibility</a>, <a href="#debian_repository-lockfile">lockfile</a>, <a href="#debian_repository-default_distro">default_distro</a>, <a href="#debian_repository-default_arch">default_arch</a>,
                             <a href="#debian_repository-python_interpreter">python_interpreter</a>, <a href="#debian_repository-python_interpreter_target">python_interpreter_target</a>)
</pre>

A rule for importing debian packages into Bazel.

This rule imports a `lockfile` and generates a new `packages.bzl` file. This is used via the `WORKSPACE` pattern:

```bazel
debian_repository(
    name = "my_debian_packages",
    default_arch = "amd64",
    default_distro = "debian11",
    lockfile = ":debian_packages.lock",
)
```

You can then reference imported packages from your `BUILD` file with:

```bazel
from("@my_debian_packages//:packages.bzl", "debian_package")
container_image(
    ...,
    debs = [
        debian_package("curl"),
    ],
)
```

| Name | Description | Type | Required | Default |
| :-------------: | :-------------: | :-------------: | :-------------: | :-------------: |
| name | a unique name for this repository. | [Name](https://bazel.build/concepts/labels) | required | |
| default_distro | distro to use as default for `debian_package` and `deb_file` | string | required | |
| default_arch | arch to use as default for `debian_package` and `deb_file` | string | required | |
| lockfile | a lockfile generated with `generate_lockfile` | [Label](https://bazel.build/concepts/labels) | required | |


### `debian_package`

<pre>
debian_package(<a href="#debian_package-name">name</a>, <a href="#debian_package-distro">distro</a>, <a href="#debian_package-arch">arch</a>)
</pre>

Download deb files of a package and all its dependencies.

**PARAMETERS**

| Name | Description | Type | Required | Default |
| :-------------: | :-------------: | :-------------: | :-------------: | :-------------: |
| name | name of package | string | required | |
| distro | distro to pull package from | string | optional | `default_distro` as specified with `debian_repository` |
| arch | arch to pull package for | string | optional | `default_arch` as specified with `debian_repository` |

### `deb_file`

<pre>
deb_file(<a href="#deb_file-name">name</a>, <a href="#deb_file-distro">distro</a>, <a href="#deb_file-arch">arch</a>)
</pre>

Download a single deb file.

**PARAMETERS**

| Name | Description | Type | Required | Default |
| :-------------: | :-------------: | :-------------: | :-------------: | :-------------: |
| name | name of package | string | required | |
| distro | distro to pull package from | string | optional | `default_distro` as specified with `debian_repository` |
| arch | arch to pull package for | string | optional | `default_arch` as specified with `debian_repository` |

### `generate_lockfile`

<pre>
generate_lockfile(<a href="#generate_lockfile-name">name</a>, <a href="#generate_lockfile-extra_args">extra_args</a>, <a href="#generate_lockfile-visibility">visibility</a>, <a href="#generate_lockfile-lockfile">lockfile</a>, <a href="#generate_lockfile-packages_file">packages_file</a>, <a href="#generate_lockfile-snapshots_file">snapshots_file</a>)
</pre>

Generates two targets for managing a lockfile:

- generate lockfile with `bazel run <name>.generate`
- update snapshots and generate lockfile with `bazel run <name>.update`

**PARAMETERS**

| Name | Description | Type | Required | Default |
| :-------------: | :-------------: | :-------------: | :-------------: | :-------------: |
| name | base name for generated targets, typically "packages" | string | required | |
| extra_args | passed to lockfile-generator | List of strings | optional | <code>[]</code> |
| visibility | passed to both the .generate and .update rules | [Visibility](https://bazel.build/concepts/visibility) | optional | <code>["//visibility:private"]</code> |
| lockfile | file to write the generated lockfile to | [Label](https://bazel.build/concepts/labels) | required | |
| snapshots_file | file defining the snapshots to use | [Label](https://bazel.build/concepts/labels) | required | |
| snapshots_file | file defining the snapshots to use | [Label](https://bazel.build/concepts/labels) | required | |
| packages_file | file defining the packages to resolve | [Label](https://bazel.build/concepts/labels) | required | |
