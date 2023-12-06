# Distronode Pytest Documentation

## About Distronode Pytest

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
