"""
To load these rules, add this to the top of your `BUILD` file:

```starlark
load("@rules_debian_packages//debian_packages:defs.bzl", ...)
```
"""

load("//debian_packages/private:lockfile.bzl", _debian_packages_lockfile = "debian_packages_lockfile")
load("//debian_packages/private:repository.bzl", _debian_packages_repository = "debian_packages_repository")

debian_packages_lockfile = _debian_packages_lockfile
debian_packages_repository = _debian_packages_repository
