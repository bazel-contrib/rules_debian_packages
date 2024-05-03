# `packages.yaml`

This file is used to define which packages to make available in your `WORKSPACE` and finely control, among other things, dependency-resolution.

## `distros`

This `list` defines from which debian-distros packages should be pulled.

Possible values:

- `debian8`
- `debian9`
- `debian10`
- `debian11`
- `debian12`

**NOTE:** It is expecting distros like `debian11` instead of codenames like `bullseye` !

## `architectures`

This `list` defines for which architectures packages should be pulled.

Possible values:

- `amd64`
- `arm64`
- `arm`
- `ppc64le`
- `s390x`

## `packages`

This `list` defines which packages to make available in your `WORKSPACE`.

## `exclude_packages`

This `list` defines which packages (and their dependencies) to exclude while resolving dependencies.

This can be used to explicitly prevent packages from being included (e.g. "when adding git do not add perl").

## `package_priorities`

This `list` defines which packages to prioritize over others when a package dependency states `either X or Y`.

## Example

```yaml
- distros: ["debian11"]
  architectures: ["amd64"]
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
