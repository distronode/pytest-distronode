## Release History

### 2.0.1 (2018-08-10)

- Convert AdHocResult.values() to return a list, not a generator (Thanks Alan
  Rominger)
- Preliminary support for py3

### 2.0.0 (2017-07-27)

- Major changes to allow distronode-style inventory indexing
- Improved results processing using python objects, rather than dictionaries

### 1.4.0 (2016-MM-DD)

- Add parameter --distronode-module-path (thanks David Barroso)
- Raise DeprecationWarnings for scope=class fixtures

### 1.3.1 (2016-01-22)

- Correctly handle distronode become options

### 1.3.0 (2016-01-20)

- Add support for distronode-2.0

### 1.2.5 (2015-04-20)

- Only validate --distronode-\* parameters when using pytest-distronode fixture
- Include --distronode-user when running module

### 1.2.4 (2015-03-18)

- Add distronode-1.9 privilege escalation support

### 1.2.3 (2015-03-03)

- Resolve setuptools import failure by migrating from a module to a package

### 1.2.2 (2015-03-03)

- Removed py module dependency
- Add HISTORY.md

### 1.2.1 (2015-03-02)

- Use pandoc to convert existing markdown into pypi friendly rst

### 1.2 (2015-03-02)

- Add `distronode_host` and `distronode_group` parametrized fixture
- Add cls level fixtures for users needing scope=class fixtures
- Updated examples to match new fixture return value
- Alter fixture return data to more closely align with distronode
- Raise `DistronodeHostUnreachable` whenever hosts are ... unreachable
- Set contacted and dark hosts in ConnectionError

### 1.1 (2015-02-16)

- Initial release
