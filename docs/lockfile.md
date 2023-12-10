<!-- Generated with Stardoc: http://skydoc.bazel.build -->


To load these rules, add this to the top of your `BUILD` file:

```starlark
load("@rules_debian_packages//debian_packages:defs.bzl", ...)
```


<a id="debian_packages_lockfile"></a>

## debian_packages_lockfile

<pre>
debian_packages_lockfile(<a href="#debian_packages_lockfile-name">name</a>, <a href="#debian_packages_lockfile-snapshots_file">snapshots_file</a>, <a href="#debian_packages_lockfile-packages_file">packages_file</a>, <a href="#debian_packages_lockfile-lock_file">lock_file</a>, <a href="#debian_packages_lockfile-mirror">mirror</a>, <a href="#debian_packages_lockfile-verbose">verbose</a>, <a href="#debian_packages_lockfile-debug">debug</a>)
</pre>

Macro that produces targets to interact with a lockfile.

Produces a target `[name].generate`, which generates a lockfile containing
packages defined in `[packages_file]` resolved against `[snapshots_file]`.

Produces a target `[name].update`, which updates the snapshots and generates
the lockfile.


Typical usage in `BUILD.bazel`:

```starlark
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



**PARAMETERS**


| Name  | Description | Default Value |
| :------------- | :------------- | :------------- |
| <a id="debian_packages_lockfile-name"></a>name |  The name of the lockfile-target.   |  none |
| <a id="debian_packages_lockfile-snapshots_file"></a>snapshots_file |  The file to read or write the debian snapshots from.   |  <code>"snapshots.yaml"</code> |
| <a id="debian_packages_lockfile-packages_file"></a>packages_file |  The file to read the desired packages from.   |  <code>"packages.yaml"</code> |
| <a id="debian_packages_lockfile-lock_file"></a>lock_file |  The file to write locked packages to.   |  <code>"packages.lock"</code> |
| <a id="debian_packages_lockfile-mirror"></a>mirror |  The debian-snapshot host to use.   |  <code>"https://snapshot.debian.org"</code> |
| <a id="debian_packages_lockfile-verbose"></a>verbose |  Enable verbose logging.   |  <code>False</code> |
| <a id="debian_packages_lockfile-debug"></a>debug |  Enable debug logging.   |  <code>False</code> |


