<!-- Generated with Stardoc: http://skydoc.bazel.build -->


To load these rules, add this to the top of your `BUILD` file:

```starlark
load("@rules_apt//apt:defs.bzl", ...)
```


<a id="apt_lockfile"></a>

## apt_lockfile

<pre>
apt_lockfile(<a href="#apt_lockfile-name">name</a>, <a href="#apt_lockfile-snapshots_file">snapshots_file</a>, <a href="#apt_lockfile-packages_file">packages_file</a>, <a href="#apt_lockfile-lock_file">lock_file</a>, <a href="#apt_lockfile-verbose">verbose</a>, <a href="#apt_lockfile-debug">debug</a>)
</pre>

Macro that produces targets to interact with a lockfile.

Produces a target `[name].generate`, which generates a lockfile containing
packages defined in `[packages_file]` resolved against `[snapshots_file]`.

Produces a target `[name].update`, which updates the snapshots and generates
the lockfile.


Typical usage in `BUILD.bazel`:

```starlark
load("@rules_apt//apt:defs.bzl", "apt_lockfile")

# Generate lockfile with:
# bazel run //path/to:apt.generate
# Update snapshots with:
# bazel run //path/to:apt.update
apt_lockfile(
    name = "apt",
    lock_file = "debian_packages.lock",
    packages_file = "debian_packages.yaml",
    snapshots_file = "debian_snapshots.yaml",
)
```



**PARAMETERS**


| Name  | Description | Default Value |
| :------------- | :------------- | :------------- |
| <a id="apt_lockfile-name"></a>name |  The name of the lockfile-target.   |  none |
| <a id="apt_lockfile-snapshots_file"></a>snapshots_file |  The file to read or write the debian snapshots from.   |  <code>"snapshots.yaml"</code> |
| <a id="apt_lockfile-packages_file"></a>packages_file |  The file to read the desired packages from.   |  <code>"packages.yaml"</code> |
| <a id="apt_lockfile-lock_file"></a>lock_file |  The file to write locked packages to.   |  <code>"packages.lock"</code> |
| <a id="apt_lockfile-verbose"></a>verbose |  Enable verbose logging.   |  <code>False</code> |
| <a id="apt_lockfile-debug"></a>debug |  Enable debug logging.   |  <code>False</code> |


