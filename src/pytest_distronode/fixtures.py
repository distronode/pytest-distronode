"""PyTest fixtures."""

import pytest


@pytest.fixture()
def distronode_adhoc(request):
    """Return an inventory initialization method."""
    plugin = request.config.pluginmanager.getplugin("distronode")

    def init_host_mgr(**kwargs):
        return plugin.initialize(request.config, request, **kwargs)

    return init_host_mgr


@pytest.fixture()
def distronode_module(distronode_adhoc):
    """Return a subclass of BaseModuleDispatcher."""
    host_mgr = distronode_adhoc()
    return getattr(host_mgr, host_mgr.options["host_pattern"])


@pytest.fixture()
def distronode_facts(distronode_module):
    """Return distronode_facts dictionary."""
    return distronode_module.setup()


@pytest.fixture()
def localhost(request):
    """Return a host manager representing localhost."""
    # NOTE: Do not use distronode_adhoc as a dependent fixture since that will assert specific command-line parameters have
    # been supplied.  In the case of localhost, the parameters are provided as kwargs below.
    plugin = request.config.pluginmanager.getplugin("distronode")
    return plugin.initialize(
        request.config,
        request,
        inventory="localhost,",
        connection="local",
        host_pattern="localhost",
    ).localhost
