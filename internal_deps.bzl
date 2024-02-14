"""Our "development" dependencies

Users should *not* need to install these. If users see a load()
statement from these, that's a bug in our distribution.
"""

load("@bazel_tools//tools/build_defs/repo:http.bzl", _http_archive = "http_archive")
load("@bazel_tools//tools/build_defs/repo:utils.bzl", "maybe")

def http_archive(name, **kwargs):
    maybe(_http_archive, name = name, **kwargs)

def rules_debian_packages_internal_deps():
    "Fetch deps needed for local development"
    http_archive(
        name = "bazel_skylib",
        sha256 = "cd55a062e763b9349921f0f5db8c3933288dc8ba4f76dd9416aac68acee3cb94",
        urls = [
            "https://mirror.bazel.build/github.com/bazelbuild/bazel-skylib/releases/download/1.5.0/bazel-skylib-1.5.0.tar.gz",
            "https://github.com/bazelbuild/bazel-skylib/releases/download/1.5.0/bazel-skylib-1.5.0.tar.gz",
        ],
    )

    http_archive(
        name = "io_bazel_stardoc",
        sha256 = "62bd2e60216b7a6fec3ac79341aa201e0956477e7c8f6ccc286f279ad1d96432",
        urls = [
            "https://mirror.bazel.build/github.com/bazelbuild/stardoc/releases/download/0.6.2/stardoc-0.6.2.tar.gz",
            "https://github.com/bazelbuild/stardoc/releases/download/0.6.2/stardoc-0.6.2.tar.gz",
        ],
    )

    http_archive(
        name = "aspect_bazel_lib",
        sha256 = "4d6010ca5e3bb4d7045b071205afa8db06ec11eb24de3f023d74d77cca765f66",
        strip_prefix = "bazel-lib-1.39.0",
        url = "https://github.com/aspect-build/bazel-lib/releases/download/v1.39.0/bazel-lib-v1.39.0.tar.gz",
    )

    http_archive(
        name = "buildifier_prebuilt",
        sha256 = "72b5bb0853aac597cce6482ee6c62513318e7f2c0050bc7c319d75d03d8a3875",
        strip_prefix = "buildifier-prebuilt-6.3.3",
        urls = [
            "http://github.com/keith/buildifier-prebuilt/archive/6.3.3.tar.gz",
        ],
    )

    http_archive(
        name = "rules_python",
        sha256 = "e85ae30de33625a63eca7fc40a94fea845e641888e52f32b6beea91e8b1b2793",
        strip_prefix = "rules_python-0.27.1",
        url = "https://github.com/bazelbuild/rules_python/releases/download/0.27.1/rules_python-0.27.1.tar.gz",
    )

    http_archive(
        name = "io_bazel_rules_docker",
        sha256 = "b1e80761a8a8243d03ebca8845e9cc1ba6c82ce7c5179ce2b295cd36f7e394bf",
        urls = ["https://github.com/bazelbuild/rules_docker/releases/download/v0.25.0/rules_docker-v0.25.0.tar.gz"],
    )

    http_archive(
        name = "rules_oci",
        sha256 = "d41d0ba7855f029ad0e5ee35025f882cbe45b0d5d570842c52704f7a47ba8668",
        strip_prefix = "rules_oci-1.4.3",
        url = "https://github.com/bazel-contrib/rules_oci/releases/download/v1.4.3/rules_oci-v1.4.3.tar.gz",
    )

    http_archive(
        name = "rules_pkg",
        sha256 = "d250924a2ecc5176808fc4c25d5cf5e9e79e6346d79d5ab1c493e289e722d1d0",
        urls = [
            "https://mirror.bazel.build/github.com/bazelbuild/rules_pkg/releases/download/0.10.1/rules_pkg-0.10.1.tar.gz",
            "https://github.com/bazelbuild/rules_pkg/releases/download/0.10.1/rules_pkg-0.10.1.tar.gz",
        ],
    )
