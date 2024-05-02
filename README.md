# Bazel rules for .deb packages

A ruleset for downloading .deb packages, and including their contents as layers in container images.

**NOTE:** this ruleset is heavily inspired by [distroless](https://github.com/GoogleContainerTools/distroless)

## Features

- Pinning of the Debian snapshot to use
- Pinning of packages using a single lockfile
- Fine-grained control over packages (and their dependencies) to exclude
- Fine-grained control over package priorities
- Compatible with [rules_oci](https://github.com/bazel-contrib/rules_oci)

## Shortcomings

- There is no way to know which packages are already contained in previous layers, thus you have to be careful how you craft your package repository.

## Installation

From the release you wish to use:
<https://github.com/sin-ack/rules_apt/releases>
copy the WORKSPACE snippet into your `WORKSPACE` file.

To use a commit rather than a release, you can point at any SHA of the repo.

For example to use commit `abc123`:

1. Replace `url = "https://github.com/sin-ack/rules_apt/releases/download/v0.1.0/rules_apt-v0.1.0.tar.gz"` with a GitHub-provided source archive like `url = "https://github.com/sin-ack/rules_apt/archive/abc123.tar.gz"`
1. Replace `strip_prefix = "rules_apt-0.1.0"` with `strip_prefix = "rules_apt-abc123"`
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

- [rules_oci](examples/rules_oci)

## Public API Docs

- [apt_lockfile](docs/lockfile.md) Generate a lockfile.
- [apt_repository](docs/repository.md) Create a package repository.
- [snapshots.yaml](docs/snapshots_yaml.md) Specify snapshot versions.
- [packages.yaml](docs/packages_yaml.md) Specify packages to provide.
