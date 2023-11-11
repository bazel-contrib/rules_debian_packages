<!-- Generated with Stardoc: http://skydoc.bazel.build -->

Public API re-exports

<a id="debian_packages_repository"></a>

## debian_packages_repository

<pre>
debian_packages_repository(<a href="#debian_packages_repository-name">name</a>, <a href="#debian_packages_repository-default_arch">default_arch</a>, <a href="#debian_packages_repository-default_distro">default_distro</a>, <a href="#debian_packages_repository-lock_file">lock_file</a>, <a href="#debian_packages_repository-repo_mapping">repo_mapping</a>)
</pre>



**ATTRIBUTES**


| Name  | Description | Type | Mandatory | Default |
| :------------- | :------------- | :------------- | :------------- | :------------- |
| <a id="debian_packages_repository-name"></a>name |  A unique name for this repository.   | <a href="https://bazel.build/concepts/labels#target-names">Name</a> | required |  |
| <a id="debian_packages_repository-default_arch"></a>default_arch |  The architecture to assume as default.   | String | required |  |
| <a id="debian_packages_repository-default_distro"></a>default_distro |  The debian-distro to assume as default.   | String | required |  |
| <a id="debian_packages_repository-lock_file"></a>lock_file |  The lockfile to generate a repository from.   | <a href="https://bazel.build/concepts/labels">Label</a> | required |  |
| <a id="debian_packages_repository-repo_mapping"></a>repo_mapping |  A dictionary from local repository name to global repository name. This allows controls over workspace dependency resolution for dependencies of this repository.&lt;p&gt;For example, an entry <code>"@foo": "@bar"</code> declares that, for any time this repository depends on <code>@foo</code> (such as a dependency on <code>@foo//some:target</code>, it should actually resolve that dependency within globally-declared <code>@bar</code> (<code>@bar//some:target</code>).   | <a href="https://bazel.build/rules/lib/dict">Dictionary: String -> String</a> | required |  |


<a id="debian_packages_lockfile"></a>

## debian_packages_lockfile

<pre>
debian_packages_lockfile(<a href="#debian_packages_lockfile-name">name</a>, <a href="#debian_packages_lockfile-snapshots_file">snapshots_file</a>, <a href="#debian_packages_lockfile-packages_file">packages_file</a>, <a href="#debian_packages_lockfile-lock_file">lock_file</a>, <a href="#debian_packages_lockfile-mirror">mirror</a>, <a href="#debian_packages_lockfile-verbose">verbose</a>, <a href="#debian_packages_lockfile-debug">debug</a>)
</pre>

Macro that generates lockfile-generator targets.

It creates two target to generate a lockfile and updating the snapshots.

You can `bazel run [name].generate` to generate a lockfile containing the
packages defined in `[packages_file]` as resolved again `[snapshots_file]`.

You can `bazel run [name].update` to update the used snapshot and regenerate
the lockfile.


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


