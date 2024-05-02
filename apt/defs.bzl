"""
To load these rules, add this to the top of your `BUILD` file:

```starlark
load("@rules_apt//apt:defs.bzl", ...)
```
"""

load("//apt/private:lockfile.bzl", _apt_lockfile = "apt_lockfile")
load("//apt/private:repository.bzl", _apt_repository = "apt_repository")

apt_lockfile = _apt_lockfile
apt_repository = _apt_repository
