# `debian_snapshots.yaml`

This file defines which snapshots to use.

It can automatically be updated by the targets provided by [debian_packages_lockfile](lockfile.md)

`main` refers to the [debian](https://snapshot.debian.org/archive/debian/)-snapshot.

`security` refers to the [debian-security](https://snapshot.debian.org/archive/debian-security/)-snapshot.

## Example

```yaml
main: 20220531T085056Z
security: 20220531T085321Z
```
