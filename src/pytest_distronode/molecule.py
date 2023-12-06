"""pytest-molecule plugin implementation."""
# pylint: disable=protected-access
from __future__ import annotations

import importlib.util
import logging
import os
import shlex
import subprocess
import sys
import warnings

from pathlib import Path

import pkg_resources
import pytest
import yaml

from distronode_compat.config import distronode_version


# Do not add molecule imports here as it does have side effects due to console
# redirection. We need to do these as lazy as possible.


molecule_spec = importlib.util.find_spec("molecule")
HAS_MOLECULE = molecule_spec is not None


logger = logging.getLogger(__name__)
counter = 0


def molecule_pytest_configure(config):
    """Pytest hook for loading our specific configuration."""
    interesting_env_vars = [
        "DISTRONODE",
        "MOLECULE",
        "DOCKER",
        "PODMAN",
        "VAGRANT",
        "VIRSH",
        "ZUUL",
    ]

    # Add extra information that may be key for debugging failures
    if hasattr(config, "_metadata"):
        for package in ["molecule"]:
            config._metadata["Packages"][package] = pkg_resources.get_distribution(
                package,
            ).version

        if "Tools" not in config._metadata:
            config._metadata["Tools"] = {}
        config._metadata["Tools"]["distronode"] = str(distronode_version())

        # Adds interesting env vars
        env = ""
        for key, value in sorted(os.environ.items()):
            for var_name in interesting_env_vars:
                if key.startswith(var_name):
                    env += f"{key}={value} "
        config._metadata["env"] = env

    # We hide DeprecationWarnings thrown by driver loading because these are
    # outside our control and worse: they are displayed even on projects that
    # have no molecule tests at all as pytest_configure() is called during
    # collection, causing spam.
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=DeprecationWarning)

        config.option.molecule = {}
        from molecule.api import drivers

        for driver in map(str, drivers()):
            config.addinivalue_line(
                "markers",
                f"{driver}: mark test to run only when {driver} is available",
            )
            config.option.molecule[driver] = {"available": True}

        config.addinivalue_line(
            "markers",
            "no_driver: mark used for scenarios that do not contain driver info",
        )

        config.addinivalue_line(
            "markers",
            "molecule: mark used by all molecule scenarios",
        )

        # validate selinux availability
        if sys.platform == "linux" and Path("/etc/selinux/config").is_file():
            try:
                import selinux  # noqa pylint: disable=unused-import,import-error,import-outside-toplevel
            except ImportError:
                logging.error(
                    "It appears that you are trying to use "
                    "molecule with a Python interpreter that does not have the "
                    "libselinux python bindings installed. These can only be "
                    "installed using your distro package manager and are specific "
                    "to each python version. Common package names: "
                    "libselinux-python python2-libselinux python3-libselinux",
                )
                # we do not re-raise this exception because missing or broken
                # selinux bindings are not guaranteed to fail molecule execution.


class MoleculeFile(pytest.File):
    """Wrapper class for molecule files."""

    def collect(self):
        """Test generator."""
        # pylint: disable=global-statement
        global counter
        if hasattr(MoleculeItem, "from_parent"):
            yield MoleculeItem.from_parent(name=f"test{counter}", parent=self)
        else:
            yield MoleculeItem(f"test{counter}", self)
        counter += 1

    def __str__(self) -> str:
        """Return test name string representation."""
        return str(self.path.relative_to(Path.cwd()))


class MoleculeItem(pytest.Item):
    """A molecule test.

    Pytest supports multiple tests per file, molecule only one "test".
    """

    def __init__(self, name, parent) -> None:
        """Construct MoleculeItem."""
        self.funcargs = {}
        super().__init__(name, parent)
        molecule_yml = self.path
        with Path(molecule_yml).open(encoding="utf-8") as stream:
            # If the molecule.yml file is empty, YAML loader returns None. To
            # simplify things down the road, we replace None with an empty
            # dict.
            data = yaml.load(stream, Loader=yaml.SafeLoader) or {}

            # we add the driver as mark
            self.molecule_driver = data.get("driver", {}).get("name", "no_driver")
            self.add_marker(self.molecule_driver)

            # check for known markers and add them
            markers = data.get("markers", [])
            if "xfail" in markers:
                self.add_marker(
                    pytest.mark.xfail(
                        reason="Marked as broken by scenario configuration.",
                    ),
                )
            if "skip" in markers:
                self.add_marker(
                    pytest.mark.skip(reason="Disabled by scenario configuration."),
                )

            # we also add platforms as marks
            for platform in data.get("platforms", []):
                platform_name = platform["name"]
                self.config.addinivalue_line(
                    "markers",
                    f"{platform_name}: molecule platform name is {platform_name}",
                )
                self.add_marker(platform_name)
            self.add_marker("molecule")
            if (
                self.config.option.molecule_unavailable_driver
                and not self.config.option.molecule[self.molecule_driver]["available"]
            ):
                self.add_marker(self.config.option.molecule_unavailable_driver)

    def runtest(self):
        """Perform effective test run."""
        folder = self.path.parent
        folders = folder.parts
        cwd = (Path(folder) / "../..").resolve()
        scenario = folders[-1]

        cmd = [sys.executable, "-m", "molecule"]
        if self.config.option.molecule_base_config:
            cmd.extend(("--base-config", self.config.option.molecule_base_config))
        if self.config.option.skip_no_git_change:
            try:
                with subprocess.Popen(
                    ["git", "diff", self.config.option.skip_no_git_change, "--", "./"],
                    cwd=cwd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    universal_newlines=True,
                ) as proc:
                    proc.wait()
                    if len(proc.stdout.readlines()) == 0:
                        pytest.skip("No change in role")
            except subprocess.CalledProcessError as exc:
                pytest.fail(
                    "Error checking git diff. Error code was: "
                    + str(exc.returncode)
                    + "\nError output was: "
                    + exc.output,
                )

        cmd.extend((self.name, "-s", scenario))
        # We append the additional options to molecule call, allowing user to
        # control how molecule is called by pytest-molecule
        opts = os.environ.get("MOLECULE_OPTS")
        if opts:
            cmd.extend(shlex.split(opts))

        if self.config.getoption("--molecule"):  # Check if --molecule option is enabled
            try:
                # Workaround for STDOUT/STDERR line ordering issue:
                # https://github.com/pytest-dev/pytest/issues/5449
                with subprocess.Popen(
                    cmd,
                    cwd=cwd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    universal_newlines=True,
                ) as proc:
                    for line in proc.stdout:
                        print(line, end="")
                    proc.wait()
                    if proc.returncode != 0:
                        pytest.fail(
                            f"Error code {proc.returncode} returned by: {' '.join(cmd)}",
                            pytrace=False,
                        )
            except subprocess.CalledProcessError as exc:
                pytest.fail(
                    f"Exception {exc} returned by: {' '.join(cmd)}",
                    pytrace=False,
                )
        else:
            pytest.skip(
                "Molecule tests are disabled",
            )  # Skip the test if --molecule option is not enabled

    def reportinfo(self):
        """Return representation of test location when in verbose mode."""
        return self.fspath, 0, f"use_case: {self.name}"

    def __str__(self) -> str:
        """Return name of the test."""
        return f"{self.name}[{self.molecule_driver}]"


class MoleculeExceptionError(Exception):
    """Custom exception for error reporting."""


class MoleculeScenario:
    """Molecule subprocess wrapper."""

    # pylint: disable=too-few-public-methods

    def __init__(self, name: str, parent_directory: Path, test_id: str) -> None:
        """Initialize the MoleculeScenario class.

        :param molecule_parent: The parent directory of 'molecule'
        :param scenario_name: The name of the molecule scenario
        :param test_id: The test id
        """
        self.parent_directory = parent_directory
        self.name = name
        self.test_id = test_id

    def test(self) -> subprocess.CompletedProcess:
        """Run molecule test for the scenario.

        :returns: The completed process
        """
        return subprocess.run(
            args=[sys.executable, "-m", "molecule", "test", "-s", self.name],
            capture_output=False,
            check=False,
            cwd=self.parent_directory,
            shell=False,
            text=True,
        )
