load("@rules_python//python/pip_install:repositories.bzl", "pip_install_dependencies")
load("//third_party:requirements.bzl", "install_deps")

def rules_debian_packages_deps():
    # Just in case rules_python dependencies weren't already fetched
    pip_install_dependencies()
    # Just in case our dependencies weren't already fetched
    install_deps()
