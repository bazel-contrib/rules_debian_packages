# Example

This workspace provides an example of using `rules_apt` with `rules_oci`.

It demonstrates how to build a container-image that is almost equivalent to `distroless/python3-debian12`.

To build the image run: `bazel build :image`

To update the debian-snapshots run: `bazel run :debian_packages.update`
