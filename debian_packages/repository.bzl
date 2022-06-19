# NOTE the following three functions are adopted from:
# https://github.com/bazelbuild/rules_python/blob/ae7a2677b3003b13d45bc9bfc25f1425bed5b407/python/pip_install/pip_repository.bzl#L6-L62

def _construct_pypath(repository_ctx):
    """Helper function to construct a PYTHONPATH.

    This allows us to run python code inside repository rule implementations.

    Args:
        repository_ctx: Handle to the repository_context.
    Returns: String of the PYTHONPATH.
    """

    # Get the root directory of these rules
    rules_root = repository_ctx.path(Label("//:BUILD.bazel")).dirname
    return str(rules_root)

def _get_python_interpreter_attr(repository_ctx):
    """A helper function for getting the `python_interpreter` attribute or it's default

    Args:
        repository_ctx (repository_ctx): Handle to the rule repository context.

    Returns:
        str: The attribute value or it's default
    """
    if repository_ctx.attr.python_interpreter:
        return repository_ctx.attr.python_interpreter

    if "win" in repository_ctx.os.name:
        return "python.exe"
    else:
        return "python3"


def _resolve_python_interpreter(repository_ctx):
    """Helper function to find the python interpreter from the common attributes

    Args:
        repository_ctx: Handle to the rule repository context.
    Returns: Python interpreter path.
    """
    python_interpreter = _get_python_interpreter_attr(repository_ctx)

    if repository_ctx.attr.python_interpreter_target != None:
        target = repository_ctx.attr.python_interpreter_target
        python_interpreter = repository_ctx.path(target)
    else:
        if "/" not in python_interpreter:
            python_interpreter = repository_ctx.which(python_interpreter)
        if not python_interpreter:
            fail("python interpreter `{}` not found in PATH".format(python_interpreter))
    return python_interpreter

def _repository_impl(repository_ctx):
    python_interpreter = _resolve_python_interpreter(repository_ctx)
    args = [
        python_interpreter,
        "-m",
        "debian_packages.generate_bazelfiles",
        "--repo",
        repository_ctx.attr.name,
        "--default-distro",
        repository_ctx.attr.default_distro,
        "--default-arch",
        repository_ctx.attr.default_arch,
        "--lock-file",
        repository_ctx.path(repository_ctx.attr.lockfile),
        "--build-file",
        "BUILD.bazel",
        "--packages-file",
        "packages.bzl",
    ]

    repository_ctx.report_progress("Parsing lockfile to starlark")

    result = repository_ctx.execute(
        args,
        environment = {"PYTHONPATH": _construct_pypath(repository_ctx)},
    )

    if result.return_code:
        fail("rules_debian_packages failed: %s (%s)" % (result.stdout, result.stderr))

    return

_repository_attrs = {
    "lockfile": attr.label(
        allow_single_file = True,
        doc = "A 'packages.lock' file",
    ),
    "default_distro": attr.string(),
    "default_arch": attr.string(),
    "python_interpreter": attr.string(
        doc = """\
The python interpreter to use. This can either be an absolute path or the name
of a binary found on the host's `PATH` environment variable. If no value is set
`python3` is defaulted for Unix systems and `python.exe` for Windows.
""",
        # NOTE: This attribute should not have a default. See `_get_python_interpreter_attr`
        # default = "python3"
    ),
    "python_interpreter_target": attr.label(
        allow_single_file = True,
        doc = """
If you are using a custom python interpreter built by another repository rule,
use this attribute to specify its BUILD target. This allows pip_repository to invoke
pip using the same interpreter as your toolchain. If set, takes precedence over
python_interpreter.
""",
    ),
}

debian_repository = repository_rule(
    implementation = _repository_impl,
    attrs = _repository_attrs,
)
