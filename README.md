# Deprecation in favor of `rules_distroless`

In order centralize efforts this repo has been deprecated in favor of [rules_distroless](https://github.com/GoogleContainerTools/rules_distroless).

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

1. [Generating a lockfile](docs/lockfile.md)
2. [Downloading packages](docs/repository.md)
3. [Consuming packages](docs/repository.md)

## Examples

- [rules_docker](examples/rules_docker/)
- [rules_oci](examples/rules_oci)

## Public API Docs

- [debian_packages_lockfile](docs/lockfile.md) Generate a lockfile.
- [debian_packages_repository](docs/repository.md) Create a package repository.
- [snapshots.yaml](docs/snapshots_yaml.md) Specify snapshot versions.
- [packages.yaml](docs/packages_yaml.md) Specify packages to provide.
