# Example

This workspace provides an example of using `rules_debian_packages`.

It demonstrates how to build a container-image that is almost equivalent to `distroless/python3-debian11`.

To build the image run: `bazel build :python_base`

To update the debian-snapshots run: `bazel run :debian_packages.update`
