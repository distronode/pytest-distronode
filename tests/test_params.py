import distronode
import pytest


# pylint: disable=unused-import
try:
    from _pytest.main import (
        EXIT_INTERRUPTED,  # type: ignore[attr-defined]
        EXIT_NOTESTSCOLLECTED,  # type: ignore[attr-defined]
        EXIT_OK,  # type: ignore[attr-defined]
        EXIT_TESTSFAILED,  # type: ignore[attr-defined]
        EXIT_USAGEERROR,  # type: ignore[attr-defined]
    )
except ImportError:
    from _pytest.main import ExitCode

    EXIT_OK = ExitCode.OK
    EXIT_TESTSFAILED = ExitCode.TESTS_FAILED
    EXIT_USAGEERROR = ExitCode.USAGE_ERROR
    EXIT_INTERRUPTED = ExitCode.INTERRUPTED
    EXIT_NOTESTSCOLLECTED = ExitCode.NO_TESTS_COLLECTED


def test_plugin_help(testdir):
    """Verifies expected output from of pytest --help."""
    result = testdir.runpytest("--help")
    result.stdout.fnmatch_lines(
        [
            # Check for the github args section header
            "pytest-distronode:",
            # Check for the specific args
            "  --inventory=DISTRONODE_INVENTORY, --distronode-inventory=DISTRONODE_INVENTORY",
            "  --host-pattern=DISTRONODE_HOST_PATTERN, --distronode-host-pattern=DISTRONODE_HOST_PATTERN",
            "  --connection=DISTRONODE_CONNECTION, --distronode-connection=DISTRONODE_CONNECTION",
            "  --user=DISTRONODE_USER, --distronode-user=DISTRONODE_USER",
            "  --check, --distronode-check",
            "  --module-path=DISTRONODE_MODULE_PATH, --distronode-module-path=DISTRONODE_MODULE_PATH",
            "  --become, --distronode-become",
            "  --become-method=DISTRONODE_BECOME_METHOD, --distronode-become-method=DISTRONODE_BECOME_METHOD",
            "  --become-user=DISTRONODE_BECOME_USER, --distronode-become-user=DISTRONODE_BECOME_USER",
            "  --ask-become-pass=DISTRONODE_ASK_BECOME_PASS, --distronode-ask-become-pass=DISTRONODE_ASK_BECOME_PASS",
            # Check for the marker in --help
            "  distronode (args)*Distronode integration",
        ],
    )


def test_plugin_markers(testdir):
    """Verifies expected output from of pytest --markers."""
    result = testdir.runpytest("--markers")
    result.stdout.fnmatch_lines(
        [
            "@pytest.mark.distronode(*args): Distronode integration",
        ],
    )


def test_report_header(testdir, option):
    """Verify the expected distronode version in the pytest report header."""
    result = testdir.runpytest(*option.args)
    assert result.ret == EXIT_NOTESTSCOLLECTED
    result.stdout.fnmatch_lines([f"distronode: {distronode.__version__}"])


def test_params_not_required_when_not_using_fixture(testdir, option):
    """Verify the distronode parameters are not required if the fixture is not used."""
    src = """
        import pytest
        def test_func():
            assert True
    """
    testdir.makepyfile(src)
    result = testdir.runpytest(*option.args)
    assert result.ret == EXIT_OK


@pytest.mark.parametrize(
    "fixture_name",
    (
        "distronode_adhoc",
        "distronode_module",
        "distronode_facts",
    ),
)
def test_params_required_when_using_fixture(testdir, option, fixture_name):
    """Verify the distronode parameters are required if the fixture is used."""
    src = f"""
        import pytest
        def test_func({fixture_name}):
            {fixture_name}
        """

    testdir.makepyfile(src)
    result = testdir.runpytest(*option.args)
    assert result.ret == EXIT_USAGEERROR
    result.stderr.fnmatch_lines(
        [
            "ERROR: Missing required parameter --distronode-host-pattern/--host-pattern",
        ],
    )


@pytest.mark.parametrize(
    "required_value_parameter",
    (
        "--distronode-inventory",
        "--inventory",
        "--distronode-host-pattern",
        "--host-pattern",
        "--distronode-connection",
        "--connection",
        "--distronode-user",
        "--user",
        "--distronode-become-method",
        "--become-method",
        "--distronode-become-user",
        "--become-user",
        "--distronode-module-path",
        "--module-path",
    ),
)
def test_param_requires_value(testdir, required_value_parameter):
    """Verifies failure when not providing a value to a parameter that requires a value."""
    result = testdir.runpytest(*[required_value_parameter])
    assert result.ret == EXIT_USAGEERROR
    result.stderr.fnmatch_lines(
        [f"*: error: argument *{required_value_parameter}*: expected one argument"],
    )


def test_params_required_with_inventory_without_host_pattern(testdir, option):
    """Verify that a host pattern is required when an inventory is supplied."""
    src = """
        import pytest
        def test_func(distronode_module):
            assert True
    """
    testdir.makepyfile(src)
    result = testdir.runpytest(*[*option.args, "--distronode-inventory", "local,"])
    assert result.ret == EXIT_USAGEERROR
    result.stderr.fnmatch_lines(
        [
            "ERROR: Missing required parameter --distronode-host-pattern/--host-pattern",
        ],
    )


@pytest.mark.requires_distronode_v2()
def test_params_required_without_inventory_with_host_pattern_v2(testdir, option):
    src = """
        import pytest
        def test_func(distronode_module):
            assert True
    """
    testdir.makepyfile(src)
    result = testdir.runpytest(*[*option.args, "--distronode-host-pattern", "all"])
    assert result.ret == EXIT_OK


def test_param_override_with_marker(testdir, option):
    src = """
        import pytest
        @pytest.mark.distronode(inventory='local,', connection='local', host_pattern='all')
        def test_func(distronode_module):
            distronode_module.ping()
    """
    testdir.makepyfile(src)
    result = testdir.runpytest(
        *[
            *option.args,
            "--tb",
            "native",
            "--distronode-inventory",
            "garbage,",
            "--distronode-host-pattern",
            "garbage",
            "--distronode-connection",
            "garbage",
        ],
    )
    assert result.ret == EXIT_OK

    # Mock assert the correct variables are set
