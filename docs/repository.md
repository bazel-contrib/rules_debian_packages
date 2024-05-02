<!-- Generated with Stardoc: http://skydoc.bazel.build -->


To load these rules, add this to the top of your `BUILD` file:

```starlark
load("@rules_apt//apt:defs.bzl", ...)
```


<a id="apt_repository"></a>

## apt_repository

<pre>
apt_repository(<a href="#apt_repository-name">name</a>, <a href="#apt_repository-default_arch">default_arch</a>, <a href="#apt_repository-default_distro">default_distro</a>, <a href="#apt_repository-lock_file">lock_file</a>, <a href="#apt_repository-repo_mapping">repo_mapping</a>)
</pre>

A repository rule to download .deb packages using Bazel's downloader.

Typical usage in `WORKSPACE.bazel`:

```starlark
load("@rules_apt//apt:defs.bzl", "apt_repository")

apt_repository(
    name = "my_debian_packages",
    default_arch = "amd64",
    default_distro = "debian12",
    lock_file = "//path/to:debian_packages.lock",
)

load("@my_debian_packages//:packages.bzl", "install_deps")

install_deps()
```


Packages can be used for `rules_oci` based container images like this:

```starlark
load("@rules_oci//oci:defs.bzl", "oci_image")
load("@my_debian_packages//:packages.bzl", "debian_package_layer")

oci_image(
    name = "my_image",
    tars = [
        debian_package_layer("busybox-static"),
    ],
)
```


**ATTRIBUTES**


| Name  | Description | Type | Mandatory | Default |
| :------------- | :------------- | :------------- | :------------- | :------------- |
| <a id="apt_repository-name"></a>name |  A unique name for this repository.   | <a href="https://bazel.build/concepts/labels#target-names">Name</a> | required |  |
| <a id="apt_repository-default_arch"></a>default_arch |  The architecture to assume as default.   | String | required |  |
| <a id="apt_repository-default_distro"></a>default_distro |  The debian-distro to assume as default.   | String | required |  |
| <a id="apt_repository-lock_file"></a>lock_file |  The lockfile to generate a repository from.   | <a href="https://bazel.build/concepts/labels">Label</a> | required |  |
| <a id="apt_repository-repo_mapping"></a>repo_mapping |  A dictionary from local repository name to global repository name. This allows controls over workspace dependency resolution for dependencies of this repository.&lt;p&gt;For example, an entry <code>"@foo": "@bar"</code> declares that, for any time this repository depends on <code>@foo</code> (such as a dependency on <code>@foo//some:target</code>, it should actually resolve that dependency within globally-declared <code>@bar</code> (<code>@bar//some:target</code>).   | <a href="https://bazel.build/rules/lib/dict">Dictionary: String -> String</a> | required |  |


