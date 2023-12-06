from unittest import mock
from unittest.mock import MagicMock

from pytest_distronode.plugin import PyTestDistronodePlugin, pytest_generate_tests


class MockItem:
    """Mock class for item object."""

    def __init__(self, fixturenames, marker=None) -> None:
        self.fixturenames = fixturenames
        self.marker = marker

    def get_closest_marker(self, marker_name):
        return self.marker


class MockConfig:
    """Mock class for config object."""

    options = {}

    def setoption(self, option_name, value):
        self.options[option_name] = value

    def getoption(self, option_name):
        return self.options.get(option_name)

    def __init__(self) -> None:
        self.options = {
            "distronode_host_pattern": "localhost",
            "distronode_inventory": "/etc/distronode/hosts",
        }


class MockPluginManager:
    """Mock class for pluginmanager object."""

    def getplugin(self, name):
        return MagicMock()


class MockMetafunc:
    """Mock class for metafunc object."""

    def __init__(self, fixturenames) -> None:
        self.fixturenames = fixturenames
        self.config = MockConfig()
        self.parametrize = MagicMock()


def test_pytest_generate_tests_with_distronode_host():
    metafunc = MagicMock()
    metafunc.fixturenames = ["distronode_host"]
    metafunc.config = MagicMock()

    # Mock config values
    metafunc.config.getoption.side_effect = {
        "distronode_host_pattern": "localhost",
        "distronode_inventory": "/etc/distronode/hosts",
    }.get

    plugin = PyTestDistronodePlugin(metafunc.config)

    # Mock Distronode host initialization
    host = MagicMock()
    host.name = "localhost"
    plugin.initialize = MagicMock(return_value={"localhost": host})

    pytest_generate_tests(metafunc)

    assert metafunc.parametrize.call_count == 1


def test_pytest_generate_tests_with_distronode_group():
    metafunc = MagicMock()
    metafunc.fixturenames = ["distronode_group"]
    config = MagicMock()
    config.pluginmanager = MagicMock()
    metafunc.config = config

    plugin = PyTestDistronodePlugin(metafunc.config)

    # Mock Distronode host initialization
    host1 = MagicMock()
    host1.name = "host1"
    group1 = MagicMock()
    group1.name = "group1"
    host1.groups = [group1]

    host2 = MagicMock()
    host2.name = "host2"
    group2 = MagicMock()
    group2.name = "group2"
    host2.groups = [group2]

    plugin.initialize = MagicMock(return_value={"host1": host1, "host2": host2})

    pytest_generate_tests(metafunc)

    assert metafunc.parametrize.call_count == 2  # Called twice for distronode_group


def test_pytest_collection_modifyitems_with_marker():
    # Mock configuration with distronode_ marker
    mock_config = MockConfig()
    mock_config.setoption("distronode_host_pattern", "some_pattern")
    mock_config.setoption("distronode_inventory", "some_inventory")

    plugin = PyTestDistronodePlugin(mock_config)
    items = [
        MockItem(
            fixturenames=["distronode_fixture"],
            marker=mock.Mock(name="distronode_marker"),
        ),
    ]

    # With the marker, ensure that assert_required_distronode_parameters is not called
    with mock.patch.object(plugin, "assert_required_distronode_parameters"):
        plugin.pytest_collection_modifyitems(None, mock_config, items)


def test_pytest_collection_modifyitems_without_marker():
    # Mock configuration without distronode_ marker
    mock_config = MockConfig()
    mock_config.setoption("distronode_host_pattern", "some_pattern")
    mock_config.setoption("distronode_inventory", "some_inventory")

    plugin = PyTestDistronodePlugin(mock_config)
    items = [MockItem(fixturenames=["distronode_adhoc"])]

    # Without the marker, ensure that assert_required_distronode_parameters is called
    with mock.patch.object(plugin, "assert_required_distronode_parameters") as mock_assert:
        plugin.pytest_collection_modifyitems(None, mock_config, items)
        mock_assert.assert_called_once()


def test_pytest_collection_modifyitems_no_fixtures():
    # Mock configuration without distronode_ marker
    mock_config = MockConfig()
    mock_config.setoption("distronode_host_pattern", "some_pattern")
    mock_config.setoption("distronode_inventory", "some_inventory")

    plugin = PyTestDistronodePlugin(mock_config)
    items = [MockItem(fixturenames=[])]

    # With no fixtures, ensure that assert_required_distronode_parameters is not called
    with mock.patch.object(plugin, "assert_required_distronode_parameters") as mock_assert:
        plugin.pytest_collection_modifyitems(None, mock_config, items)
        mock_assert.assert_not_called()
