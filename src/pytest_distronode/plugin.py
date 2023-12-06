"""PyTest Distronode Plugin."""
from __future__ import annotations

import contextlib
import logging
import subprocess

from typing import TYPE_CHECKING

import distronode
import distronode.constants
import distronode.errors
import distronode.utils
import distronode.utils.display
import pytest

from pytest_distronode.fixtures import (
    distronode_adhoc,
    distronode_facts,
    distronode_module,
    localhost,
)
from pytest_distronode.host_manager import get_host_manager

from .molecule import HAS_MOLECULE, MoleculeFile, MoleculeScenario
from .units import inject, inject_only


if TYPE_CHECKING:
    from pathlib import Path

    from _pytest.nodes import Node

logger = logging.getLogger(__name__)

# Silence linters for imported fixtures
# pylint: disable=pointless-statement, no-member
(distronode_adhoc, distronode_module, distronode_facts, localhost)

log_map = {
    0: logging.CRITICAL,
    1: logging.ERROR,
    2: logging.WARNING,
    3: logging.INFO,
    4: logging.DEBUG,
}
OUR_FIXTURES = ("distronode_adhoc", "distronode_module", "distronode_facts")


def pytest_addoption(parser):
    """Add options to control distronode."""
    group = parser.getgroup("pytest-distronode")
    group.addoption(
        "--inventory",
        "--distronode-inventory",
        action="store",
        dest="distronode_inventory",
        default=distronode.constants.DEFAULT_HOST_LIST,
        metavar="DISTRONODE_INVENTORY",
        help="distronode inventory file URI (default: %(default)s)",
    )
    group.addoption(
        "--extra-inventory",
        "--distronode-extra-inventory",
        action="store",
        dest="distronode_extra_inventory",
        default=None,
        metavar="DISTRONODE_EXTRA_INVENTORY",
        help="distronode extra inventory file URI (default: %(default)s)",
    )
    group.addoption(
        "--host-pattern",
        "--distronode-host-pattern",
        action="store",
        dest="distronode_host_pattern",
        default=None,
        metavar="DISTRONODE_HOST_PATTERN",
        help="distronode host pattern (default: %(default)s)",
    )
    group.addoption(
        "--limit",
        "--distronode-limit",
        action="store",
        dest="distronode_subset",
        default=distronode.constants.DEFAULT_SUBSET,
        metavar="DISTRONODE_SUBSET",
        help="further limit selected hosts to an additional pattern",
    )
    group.addoption(
        "--connection",
        "--distronode-connection",
        action="store",
        dest="distronode_connection",
        default=distronode.constants.DEFAULT_TRANSPORT,
        help="connection type to use (default: %(default)s)",
    )
    group.addoption(
        "--user",
        "--distronode-user",
        action="store",
        dest="distronode_user",
        default=distronode.constants.DEFAULT_REMOTE_USER,
        help="connect as this user (default: %(default)s)",
    )
    group.addoption(
        "--check",
        "--distronode-check",
        action="store_true",
        dest="distronode_check",
        default=False,
        help="don't make any changes; instead, try to predict some of the changes that may occur",
    )
    group.addoption(
        "--module-path",
        "--distronode-module-path",
        action="store",
        dest="distronode_module_path",
        default=distronode.constants.DEFAULT_MODULE_PATH,
        help="specify path(s) to module library (default: %(default)s)",
    )

    # become privilege escalation
    group.addoption(
        "--become",
        "--distronode-become",
        action="store_true",
        dest="distronode_become",
        default=distronode.constants.DEFAULT_BECOME,
        help="run operations with become, nopasswd implied (default: %(default)s)",
    )
    group.addoption(
        "--become-method",
        "--distronode-become-method",
        action="store",
        dest="distronode_become_method",
        default=distronode.constants.DEFAULT_BECOME_METHOD,
        help="privilege escalation method to use (default: %(default)s)",
    )

    group.addoption(
        "--become-user",
        "--distronode-become-user",
        action="store",
        dest="distronode_become_user",
        default=distronode.constants.DEFAULT_BECOME_USER,
        help="run operations as this user (default: %(default)s)",
    )
    group.addoption(
        "--ask-become-pass",
        "--distronode-ask-become-pass",
        action="store",
        dest="distronode_ask_become_pass",
        default=distronode.constants.DEFAULT_BECOME_ASK_PASS,
        help="ask for privilege escalation password (default: %(default)s)",
    )
    group.addoption(
        "--distronode-unit-inject-only",
        action="store_true",
        default=False,
        help="Enable support for distronode collection unit tests by only injecting existing DISTRONODE_COLLECTIONS_PATH.",
    )
    group.addoption(
        "--molecule",
        action="store_true",
        default=False,
        help="Enable support for running discovered molecule scenarios from pytest.",
    )
    group.addoption(
        "--molecule_unavailable_driver",
        action="store",
        default=None,
        help="What marker to add to molecule scenarios when driver is ",
    )
    group.addoption(
        "--molecule_base_config",
        action="store",
        default=None,
        help="Path to the molecule base config file. The value of this option is ",
    )
    group.addoption(
        "--skip_no_git_change",
        action="store",
        default=None,
        help="Commit to use as a reference for this test. If the role wasn't",
    )
    # Add github marker to --help
    parser.addini("distronode", "Distronode integration", "args")


def pytest_configure(config):
    """Validate --distronode-* parameters."""
    config.addinivalue_line("markers", "distronode(**kwargs): Distronode integration")

    # Enable connection debugging
    if config.option.verbose > 0:
        if hasattr(distronode.utils, "VERBOSITY"):
            distronode.utils.VERBOSITY = int(config.option.verbose)
        else:
            distronode.utils.display.verbosity = int(config.option.verbose)

    # Configure the logger.
    level = log_map.get(config.option.verbose)
    logging.basicConfig(level=level)
    logging.debug("Logging initialized")

    assert config.pluginmanager.register(PyTestDistronodePlugin(config), "distronode")

    if config.option.distronode_unit_inject_only:
        inject_only()
    else:
        start_path = config.invocation_params.dir
        inject(start_path)


def pytest_collect_file(
    file_path: Path | None,
    parent: pytest.Collector,
) -> Node | None:
    """Transform each found molecule.yml into a pytest test."""
    if not parent.config.option.molecule:
        return None
    if not HAS_MOLECULE:
        pytest.exit(
            f"molecule not installed or found, unable to collect test {file_path}",
        )
        return None
    if file_path and file_path.is_symlink():
        return None
    if file_path and file_path.name == "molecule.yml":
        return MoleculeFile.from_parent(path=file_path, parent=parent)
    return None


def pytest_generate_tests(metafunc):
    """Generate tests when specific `distronode_*` fixtures are used by tests."""
    if "distronode_host" in metafunc.fixturenames:
        # assert required --distronode-* parameters were used
        PyTestDistronodePlugin.assert_required_distronode_parameters(metafunc.config)
        try:
            plugin = metafunc.config.pluginmanager.getplugin("distronode")
            hosts = plugin.initialize(
                config=plugin.config,
                pattern=metafunc.config.getoption("distronode_host_pattern"),
            )
        except distronode.errors.DistronodeError as exception:
            raise pytest.UsageError(exception)

        # Return the host name as a string
        metafunc.parametrize("distronode_host", iter(hosts[h] for h in hosts))

    if "distronode_group" in metafunc.fixturenames:
        # assert required --distronode-* parameters were used
        PyTestDistronodePlugin.assert_required_distronode_parameters(metafunc.config)
        try:
            plugin = metafunc.config.pluginmanager.getplugin("distronode")
            hosts = plugin.initialize(
                config=plugin.config,
                pattern=metafunc.config.getoption("distronode_host_pattern"),
            )
        except distronode.errors.DistronodeError as exception:
            raise pytest.UsageError(exception)
        groups = hosts.options["inventory_manager"].list_groups()
        extra_groups = hosts.get_extra_inventory_groups()
        # Return the group name as a string
        metafunc.parametrize("distronode_group", iter(hosts[g] for g in groups))
        metafunc.parametrize("distronode_group", iter(hosts[g] for g in extra_groups))

    if "molecule_scenario" in metafunc.fixturenames:
        if not HAS_MOLECULE:
            pytest.exit("molecule not installed or found.")

        # Find all molecule scenarios not gitignored
        rootpath = metafunc.config.rootpath

        scenarios = []

        candidates = list(rootpath.glob("**/molecule/*/molecule.yml"))
        command = ["git", "check-ignore", *candidates]
        with contextlib.suppress(subprocess.CalledProcessError, FileNotFoundError):
            proc = subprocess.run(
                args=command,
                capture_output=True,
                check=True,
                text=True,
                shell=False,
            )

        try:
            ignored = proc.stdout.splitlines()
            scenario_paths = [
                candidate for candidate in candidates if str(candidate) not in ignored
            ]
        except NameError:
            scenario_paths = candidates

        for fs_entry in scenario_paths:
            scenario = fs_entry.parent
            molecule_parent = scenario.parent.parent
            scenarios.append(
                MoleculeScenario(
                    parent_directory=molecule_parent,
                    name=scenario.name,
                    test_id=f"{molecule_parent.name}-{scenario.name}",
                ),
            )
        if not scenarios:
            pytest.exit(f"No molecule scenarios found in: {rootpath}")
        metafunc.parametrize(
            "molecule_scenario",
            scenarios,
            ids=[scenario.test_id for scenario in scenarios],
        )


class PyTestDistronodePlugin:
    """Distronode PyTest Plugin Class."""

    def __init__(self, config) -> None:
        """Initialize plugin."""
        self.config = config

    def pytest_report_header(self):
        """Return the version of distronode."""
        return f"distronode: {distronode.__version__}"

    def pytest_collection_modifyitems(self, session, config, items):
        """Validate --distronode-* parameters."""
        uses_distronode_fixtures = False
        for item in items:
            if not hasattr(item, "fixturenames"):
                continue

            for fixture_name in item.fixturenames:
                if fixture_name in OUR_FIXTURES:
                    uses_distronode_fixtures = True
                    break

                # ignore any normal fixtures that have definitions to avoid miss activations
                if (
                    hasattr(item, "_fixtureinfo")
                    and hasattr(item._fixtureinfo, "name2fixturedefs")
                    and fixture_name in item._fixtureinfo.name2fixturedefs
                ):
                    continue
                logger.error(
                    "Found %s fixture which seem to have no definition.",
                    fixture_name,
                )

        if uses_distronode_fixtures:
            # assert required --distronode-* parameters were used
            self.assert_required_distronode_parameters(config)

    def _load_distronode_config(self, config):
        """Load distronode configuration from command-line."""
        option_names = [
            "distronode_inventory",
            "distronode_extra_inventory",
            "distronode_host_pattern",
            "distronode_connection",
            "distronode_user",
            "distronode_module_path",
            "distronode_become",
            "distronode_become_method",
            "distronode_become_user",
            "distronode_ask_become_pass",
            "distronode_subset",
        ]

        kwargs = {}

        # Load command-line supplied values
        for key in option_names:
            short_key = key[8:]
            kwargs[short_key] = config.getoption(key)

        # normalize distronode.distronode_become options
        kwargs["become"] = kwargs.get("become") or distronode.constants.DEFAULT_BECOME
        kwargs["become_user"] = (
            kwargs.get("become_user") or distronode.constants.DEFAULT_BECOME_USER
        )
        kwargs["ask_become_pass"] = (
            kwargs.get("ask_become_pass") or distronode.constants.DEFAULT_BECOME_ASK_PASS
        )

        return kwargs

    def _load_request_config(self, request):
        """Load distronode configuration from decorator kwargs."""
        kwargs = {}

        # Override options from @pytest.mark.distronode
        marker = request.node.get_closest_marker("distronode")
        if marker:
            kwargs = marker.kwargs

        return kwargs

    def initialize(self, config=None, request=None, **kwargs):
        """Return an initialized Distronode Host Manager instance."""
        distronode_cfg = {}
        # merge command-line configuration options
        if config is not None:
            distronode_cfg.update(self._load_distronode_config(config))
        # merge pytest request configuration options
        if request is not None:
            distronode_cfg.update(self._load_request_config(request))
        # merge in provided kwargs
        distronode_cfg.update(kwargs)
        return get_host_manager(**distronode_cfg)

    @staticmethod
    def assert_required_distronode_parameters(config):
        """Assert whether the required --distronode-* parameters were provided."""
        errors = []

        # Verify --distronode-host-pattern was provided
        distronode_hostname = config.getoption("distronode_host_pattern")
        if distronode_hostname is None or distronode_hostname == "":
            errors.append(
                "Missing required parameter --distronode-host-pattern/--host-pattern",
            )

        # NOTE: I don't think this will ever catch issues since distronode_inventory
        # defaults to '/etc/distronode/hosts'
        # Verify --distronode-inventory was provided
        distronode_inventory = config.getoption("distronode_inventory")
        if distronode_inventory is None or distronode_inventory == "":
            errors.append(
                "Unable to find an inventory file, specify one with the --distronode-inventory/--inventory "
                "parameter.",
            )

        if errors:
            raise pytest.UsageError(*errors)
