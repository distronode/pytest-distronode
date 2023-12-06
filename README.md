# pytest-distronode

[![Build Status](https://github.com/distronode/pytest-distronode/actions/workflows/tox.yml/badge.svg)](https://github.com/distronode/pytest-distronode/actions/workflows/tox.yml)
[![Version](https://img.shields.io/pypi/v/pytest-distronode.svg)](https://pypi.python.org/pypi/pytest-distronode/)
[![License](https://img.shields.io/pypi/l/pytest-distronode.svg)](https://pypi.python.org/pypi/pytest-distronode/)
[![Supported Python Versions](https://img.shields.io/pypi/pyversions/pytest-distronode.svg)](https://pypi.python.org/pypi/pytest-distronode/)

The `pytest-distronode` plugin is designed to provide seamless integration between
`pytest` and `Distronode`, allowing you to efficiently run and test Distronode-related
tasks and scenarios within your pytest test suite. This plugin enhances the
testing workflow by offering three distinct pieces of functionality:

1. **Unit Testing for Distronode Collections**: This feature aids in running unit
   tests for `Distronode collections` using `pytest`. It allows you to validate the
   behavior of your Distronode `modules` and `roles` in isolation, ensuring that
   each component functions as expected.

2. **Molecule Scenario Integration**: The plugin assists in running Molecule
   `scenarios` using `pytest`. This integration streamlines the testing of
   Distronode roles and playbooks across different environments, making it easier
   to identify and fix issues across diverse setups.

3. **Distronode Integration for Pytest Tests**: With this functionality, you can
   seamlessly use `Distronode` from within your `pytest` tests. This opens up
   possibilities to interact with Distronode components and perform tasks like
   provisioning resources, testing configurations, and more, all while
   leveraging the power and flexibility of pytest.

## Supported Distronode

Pytest Distronode will only support versions of **python** and **distronode-core**
which are under
[active upstream support](https://docs.distronode.com/distronode/latest/reference_appendices/release_and_maintenance.html#release-schedule)
which currently translates to:

- Python 3.9 or newer
- Distronode-core 2.14 or newer

## Installation

Install this plugin using `pip`:

```
pip install pytest-distronode
```

## Getting Started

### Unit Testing for Distronode Collections

The `pytest-distronode-units` plugin allows distronode collection's unit tests to be
run with only `pytest`. It offers a focused approach to testing individual
Distronode modules. With this plugin, you can write and execute unit tests
specifically for Distronode modules, ensuring the accuracy and reliability of your
module code. This is particularly useful for verifying the correctness of module
behavior in isolation.

To use `pytest-distronode-units`, follow these steps:

1. Install the plugin using pip:

```
pip install pytest-distronode
```

2. Ensure you have Python 3.9 or greater, distronode-core, and pyyaml installed.

3. Depending on your preferred directory structure, you can clone collections
   into the appropriate paths.

   - **Collection Tree Approach**: The preferred approach is to clone the
     collections being developed into it's proper collection tree path. This
     eliminates the need for any symlinks and other collections being developed
     can be cloned into the same tree structure.

     ```
     git clone <repo> collections/distronode_collections/<namespace>/<name>
     ```

     Note: Run `pytest` in the root of the collection directory, adjacent to the
     collection's `galaxy.yml` file.

   - **Shallow Tree Approach**:

     ```
     git clone <repo>
     ```

     Notes:

     - Run `pytest` in the root of the collection directory, adjacent to the
       collection's `galaxy.yml` file.
     - A collections directory will be created in the repository directory, and
       collection content will be linked into it.

4. Execute the unit tests using pytest: `pytest tests`

### Help

The following may be added to the collections' `pyproject.toml` file to limit
warnings and set the default path for the collection's tests

```
[tool.pytest.ini_options]
testpaths = [
    "tests",
]
filterwarnings = [
    'ignore:DistronodeCollectionFinder has already been configured',
]
```

Information from the `galaxy.yml` file is used to build the `collections`
directory structure and link the contents. The `galaxy.yml` file should reflect
the correct collection namespace and name.

One way to detect issues without running the tests is to run:

```
pytest --collect-only
```

The follow errors may be seen:

```
E   ModuleNotFoundError: No module named 'distronode_collections'
```

- Check the `galaxy.yml` file for an accurate namespace and name
- Ensure `pytest` is being run from the collection's root directory, adjacent to
  the `galaxy.yml`

```
HINT: remove __pycache__ / .pyc files and/or use a unique basename for your test file modules
```

## Molecule Scenario Integration

This functionality assists in running Molecule `scenarios` using `pytest`. It
enables pytest discovery of all `molecule.yml` files inside the codebase and
runs them as pytest tests. It allows you to include Molecule scenarios as part
of your pytest test suite, allowing you to thoroughly test your Distronode roles
and playbooks across different scenarios and environments.

## Running molecule scenarios using pytest

Molecule scenarios can be tested using 2 different methods if molecule is
installed.

**Recommended:**

Add a `test_integration.py` file to the `tests/integration` directory of the
distronode collection:

```
"""Tests for molecule scenarios."""
from __future__ import absolute_import, division, print_function

from pytest_distronode.molecule import MoleculeScenario


def test_integration(molecule_scenario: MoleculeScenario) -> None:
    """Run molecule for each scenario.

    :param molecule_scenario: The molecule scenario object
    """
    proc = molecule_scenario.test()
    assert proc.returncode == 0
```

The `molecule_scenario` fixture provides parameterized molecule scenarios
discovered in the collection's `extensions/molecule` directory, as well as other
directories within the collection.

`molecule test -s <scenario>` will be run for each scenario and a completed
subprocess returned from the `test()` call.

**Legacy:**

Run molecule with the `--molecule` command line parameter to inject each
molecule directory found in the current working directory. Each scenario will be
injected as an external test in the the tests available for pytest. Due to the
nature of this approach, the molecule scenarios are not represented as python
tests and may not show in the IDE's pytest test tree.

To run Molecule scenarios using pytest, follow these steps:

1. Install the `pytest-distronode` plugin using pip:

```
pip install pytest-distronode
```

2. Execute pytest to run Molecule scenarios: `pytest`

## Distronode Integration for Pytest Tests

The `distronode_module`, `distronode_adhoc`, `localhost`, and `distronode_facts` fixtures
are provided to help you integrate Distronode functionalities into your pytest
tests. These fixtures allow you to interact with Distronode modules, run commands
on localhost, fetch Distronode facts, and more.

## Fixtures and helpers for use in tests

Here's a quick overview of the available fixtures:

- `distronode_module`: Allows you to call Distronode modules directly within your test
  functions.
- `distronode_adhoc`: Provides a function to initialize a `HostManager` object to
  work with Distronode inventory.
- `localhost`: A convenience fixture for running Distronode modules that typically
  run on the local machine.
- `distronode_facts`: Returns a JSON structure representing system facts for the
  associated inventory.

### Usage

Once installed, the following `pytest` command-line parameters are available:

```bash
pytest \
    [--inventory <path_to_inventory>] \
    [--extra-inventory <path_to_extra_inventory>] \
    [--host-pattern <host-pattern>] \
    [--connection <plugin>] \
    [--module-path <path_to_modules] \
    [--user <username>] \
    [--become] \
    [--become-user <username>] \
    [--become-method <method>] \
    [--ask-become-pass] \
    [--limit <limit>] \
    [--distronode-unit-inject-only] \
    [--molecule] \
    [--molecule-unavailable-driver] \
    [--skip-no-git-change] \
    [--check]
```

### Inventory

Using distronode first starts with defining your inventory. This can be done in
several ways, but to start, we'll use the `distronode_adhoc` fixture.

```python
def test_my_inventory(distronode_adhoc):
    hosts = distronode_adhoc()
```

In the example above, the `hosts` variable is an instance of the `HostManager`
class and describes your distronode inventory. For this to work, you'll need to
tell `distronode` where to find your inventory. Inventory can be anything supported
by distronode, which includes an
[INI file](http://docs.distronode.com/distronode/latest/intro_inventory.html) or an
executable script that returns
[properly formatted JSON](http://docs.distronode.com/distronode/latest/intro_dynamic_inventory.html).
For example,

```bash
pytest --inventory my_inventory.ini --host-pattern all
```

or

```bash
pytest --inventory path/to/my/script.py --host-pattern webservers
```

or

```bash
pytest --inventory one.example.com,two.example.com --host-pattern all
```

In the above examples, the inventory provided at runtime will be used in all
tests that use the `distronode_adhoc` fixture. A more realistic scenario may
involve using different inventory files (or host patterns) with different tests.
To accomplish this, the fixture `distronode_adhoc` allows you to customize the
inventory parameters. Read on for more detail on using the `distronode_adhoc`
fixture.

### Extra Inventory

Using distronode first starts with defining your extra inventory. This feature was
added in version 2.3.0, and is intended to allow the user to work with two
different inventories. This can be done in several ways, but to start, we'll use
the `distronode_adhoc` fixture.

For example,

```bash
pytest --inventory my_inventory.ini --extra-inventory my_second_inventory.ini --host-pattern host_in_second_inventory
```

#### Fixture `distronode_adhoc`

The `distronode_adhoc` fixture returns a function used to initialize a
`HostManager` object. The `distronode_adhoc` fixture will default to parameters
supplied to the `pytest` command-line, but also allows one to provide keyword
arguments used to initialize the inventory.

The example below demonstrates basic usage with options supplied at run-time to
`pytest`.

```python
def test_all_the_pings(distronode_adhoc):
    distronode_adhoc().all.ping()
```

The following example demonstrates available keyword arguments when creating a
`HostManager` object.

```python
def test_uptime(distronode_adhoc):
    # take down the database
    distronode_adhoc(inventory='db1.example.com,', user='ec2-user',
        become=True, become_user='root').all.command('reboot')
```

The `HostManager` object returned by the `distronode_adhoc()` function provides
numerous ways of calling distronode modules against some, or all, of the inventory.
The following demonstrates sample usage.

```python
def test_host_manager(distronode_adhoc):
    hosts = distronode_adhoc()

    # __getitem__
    hosts['all'].ping()
    hosts['localhost'].ping()

    # __getattr__
    hosts.all.ping()
    hosts.localhost.ping()

    # Supports [distronode host patterns](http://docs.distronode.com/distronode/latest/intro_patterns.html)
    hosts['webservers:!phoenix'].ping()  # all webservers that are not in phoenix
    hosts[0].ping()
    hosts[0:2].ping()

    assert 'one.example.com' in hosts

    assert hasattr(hosts, 'two.example.com')

    for a_host in hosts:
        a_host.ping()
```

#### Fixture `localhost`

The `localhost` fixture is a convenience fixture that surfaces a
`ModuleDispatcher` instance for distronode host running `pytest`. This is
convenient when using distronode modules that typically run on the local machine,
such as cloud modules (ec2, gce etc...).

```python
def test_do_something_cloudy(localhost, distronode_adhoc):
    """Deploy an ec2 instance using multiple fixtures."""
    params = dict(
        key_name='some_key',
        instance_type='t2.micro',
        image='ami-123456',
        wait=True,
        group='webservers',
        count=1,
        vpc_subnet_id='subnet-29e63245',
        assign_public_ip=True,
    )

    # Deploy an ec2 instance from localhost using the `distronode_adhoc` fixture
    distronode_adhoc(inventory='localhost,', connection='local').localhost.ec2(**params)

    # Deploy an ec2 instance from localhost using the `localhost` fixture
    localhost.ec2(**params)
```

#### Fixture `distronode_module`

The `distronode_module` fixture allows tests and fixtures to call
[distronode modules](http://docs.distronode.com/modules.html). Unlike the
`distronode_adhoc` fixture, this fixture only uses the options supplied to `pytest`
at run time.

A very basic example demonstrating the distronode
[`ping` module](http://docs.distronode.com/ping_module.html):

```python
def test_ping(distronode_module):
    distronode_module.ping()
```

A more involved example of updating the sshd configuration, and restarting the
service.

```python
def test_sshd_config(distronode_module):

    # update sshd MaxSessions
    contacted = distronode_module.lineinfile(
        dest="/etc/ssh/sshd_config",
        regexp="^#?MaxSessions .*",
        line="MaxSessions 150")
    )

    # assert desired outcome
    for (host, result) in contacted.items():
        assert 'failed' not in result, result['msg']
        assert 'changed' in result

    # restart sshd
    contacted = distronode_module.service(
        name="sshd",
        state="restarted"
    )

    # assert successful restart
    for (host, result) in contacted.items():
        assert 'changed' in result and result['changed']
        assert result['name'] == 'sshd'

    # do other stuff ...
```

#### Fixture `distronode_facts`

The `distronode_facts` fixture returns a JSON structure representing the system
facts for the associated inventory. Sample fact data is available in the
[distronode documentation](http://docs.distronode.com/playbooks_variables.html#information-discovered-from-systems-facts).

Note, this fixture is provided for convenience and could easily be called using
`distronode_module.setup()`.

A systems facts can be useful when deciding whether to skip a test ...

```python
def test_something_with_amazon_ec2(distronode_facts):
    for facts in distronode_facts:
        if 'ec2.internal' != facts['distronode_domain']:
            pytest.skip("This test only applies to ec2 instances")

```

Additionally, since facts are just distronode modules, you could inspect the
contents of the `ec2_facts` module for greater granularity ...

```python

def test_terminate_us_east_1_instances(distronode_adhoc):

    for facts in distronode_adhoc().all.ec2_facts():
        if facts['distronode_ec2_placement_region'].startswith('us-east'):
            '''do some testing'''
```

#### Parameterize with `pytest.mark.distronode`

Perhaps the `--distronode-inventory=<inventory>` includes many systems, but you
only wish to interact with a subset. The `pytest.mark.distronode` marker can be
used to modify the `pytest-distronode` command-line parameters for a single test.
Please note, the fixture `distronode_adhoc` is the prefer mechanism for interacting
with distronode inventory within tests.

For example, to interact with the local system, you would adjust the
`host_pattern` and `connection` parameters.

```python
@pytest.mark.distronode(host_pattern='local,', connection='local')
def test_copy_local(distronode_module):

    # create a file with random data
    contacted = distronode_module.copy(
        dest='/etc/motd',
        content='PyTest is amazing!',
        owner='root',
        group='root',
        mode='0644',
    )

    # assert only a single host was contacted
    assert len(contacted) == 1, \
        "Unexpected number of hosts contacted (%d != %d)" % \
        (1, len(contacted))

    assert 'local' in contacted

    # assert the copy module reported changes
    assert 'changed' in contacted['local']
    assert contacted['local']['changed']
```

Note, the parameters provided by `pytest.mark.distronode` will apply to all class
methods.

```python
@pytest.mark.distronode(host_pattern='local,', connection='local')
class Test_Local(object):
    def test_install(self, distronode_module):
        '''do some testing'''
    def test_template(self, distronode_module):
        '''do some testing'''
    def test_service(self, distronode_module):
        '''do some testing'''
```

#### Inspecting results

When using the `distronode_adhoc`, `localhost` or `distronode_module` fixtures, the
object returned will be an instance of class `AdHocResult`. The `AdHocResult`
class can be inspected as follows:

```python

def test_adhoc_result(distronode_adhoc):
    contacted = distronode_adhoc(inventory=my_inventory).command("date")

    # As a dictionary
    for (host, result) in contacted.items():
        assert result.is_successful, "Failed on host %s" % host
    for result in contacted.values():
        assert result.is_successful
    for host in contacted.keys():
        assert host in ['localhost', 'one.example.com']

    assert contacted.localhost.is_successful

    # As a list
    assert len(contacted) > 0
    assert 'localhost' in contacted

    # As an iterator
    for result in contacted:
        assert result.is_successful

    # With __getattr__
    assert contacted.localhost.is_successful

    # Or __getitem__
    assert contacted['localhost'].is_successful
```

Using the `AdHocResult` object provides ways to conveniently access results for
different hosts involved in the distronode adhoc command. Once the specific host
result is found, you may inspect the result of the distronode adhoc command on that
use by way of the `ModuleResult` interface. The `ModuleResult` class represents
the dictionary returned by the distronode module for a particular host. The
contents of the dictionary depend on the module called.

The `ModuleResult` interface provides some convenient properties to determine
the success of the module call. Examples are included below.

```python

def test_module_result(localhost):
    contacted = localhost.command("find /tmp")

    assert contacted.localhost.is_successful
    assert contacted.localhost.is_ok
    assert contacted.localhost.is_changed
    assert not contacted.localhost.is_failed

    contacted = localhost.shell("exit 1")
    assert contacted.localhost.is_failed
    assert not contacted.localhost.is_successful
```

The contents of the JSON returned by an distronode module differs from module to
module. For guidance, consult the documentation and examples for the specific
[distronode module](http://docs.distronode.com/modules_by_category.html).

#### Exception handling

If `distronode` is unable to connect to any inventory, an exception will be raised.

```python
@pytest.mark.distronode(inventory='unreachable.example.com,')
def test_shutdown(distronode_module):

    # attempt to ping a host that is down (or doesn't exist)
    pytest.raises(pytest_distronode.DistronodeHostUnreachable):
        distronode_module.ping()
```

Sometimes, only a single host is unreachable, and others will have properly
returned data. The following demonstrates how to catch the exception, and
inspect the results.

```python
@pytest.mark.distronode(inventory='good:bad')
def test_inventory_unreachable(distronode_module):
    exc_info = pytest.raises(pytest_distronode.DistronodeHostUnreachable, distronode_module.ping)
    (contacted, dark) = exc_info.value.results

    # inspect the JSON result...
    for (host, result) in contacted.items():
        assert result['ping'] == 'pong'

    for (host, result) in dark.items():
        assert result['failed'] == True
```

## Contributing

Contributions are very welcome. Tests can be run with
[tox](https://tox.wiki/en/latest/), please ensure the coverage at least stays
the same before you submit a pull request.

## License

Distributed under the terms of the [MIT](https://opensource.org/license/mit/)
license, "pytest-distronode" is free and open source software

## Issues

If you encounter any problems, please
[file an issue](https://github.com/pycontribs/pytest-distronode/issues) along with
a detailed description.
