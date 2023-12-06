# pylint: disable=unused-import


try:
    from _pytest.main import EXIT_OK  # type: ignore
except ImportError:
    from _pytest.main import ExitCode

    EXIT_OK = ExitCode.OK


def test_distronode_adhoc(testdir, option):
    src = """
        import pytest
        import types
        from pytest_distronode.host_manager import BaseHostManager
        def test_func(distronode_adhoc):
            assert isinstance(distronode_adhoc, types.FunctionType)
            assert isinstance(distronode_adhoc(), BaseHostManager)
    """
    testdir.makepyfile(src)
    result = testdir.runpytest(
        *[
            *option.args,
            "--distronode-inventory",
            str(option.inventory),
            "--distronode-host-pattern",
            "local",
        ],
    )
    assert result.ret == EXIT_OK
    assert result.parseoutcomes()["passed"] == 1


def test_distronode_module(testdir, option):
    src = """
        import pytest
        from pytest_distronode.module_dispatcher import BaseModuleDispatcher
        def test_func(distronode_module):
            assert isinstance(distronode_module, BaseModuleDispatcher)
    """
    testdir.makepyfile(src)
    result = testdir.runpytest(
        *[
            *option.args,
            "--distronode-inventory",
            str(option.inventory),
            "--distronode-host-pattern",
            "local",
        ],
    )
    assert result.ret == EXIT_OK
    assert result.parseoutcomes()["passed"] == 1


def test_distronode_facts(testdir, option):
    src = """
        import pytest
        from pytest_distronode.results import AdHocResult
        def test_func(distronode_facts):
            assert isinstance(distronode_facts, AdHocResult)
    """
    testdir.makepyfile(src)
    result = testdir.runpytest(
        *[
            *option.args,
            "--distronode-inventory",
            str(option.inventory),
            "--distronode-host-pattern",
            "local",
        ],
    )
    assert result.ret == EXIT_OK
    assert result.parseoutcomes()["passed"] == 1


def test_localhost(testdir, option):
    src = """
        import pytest
        from pytest_distronode.module_dispatcher import BaseModuleDispatcher
        def test_func(localhost):
            assert isinstance(localhost, BaseModuleDispatcher)
    """
    testdir.makepyfile(src)
    result = testdir.runpytest(*option.args)
    assert result.ret == EXIT_OK
    assert result.parseoutcomes()["passed"] == 1
