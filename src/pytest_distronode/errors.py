"""Defines pytest-distronode exception classes."""

import distronode.errors


class DistronodeNoHostsMatch(distronode.errors.DistronodeError):
    """Sub-class DistronodeError when no hosts match."""


class DistronodeConnectionFailure(distronode.errors.DistronodeError):
    """Sub-class DistronodeError when connection failures occur."""

    def __init__(self, msg, dark=None, contacted=None) -> None:
        """Initialize connection error class."""
        super().__init__(msg)
        self.contacted = contacted
        self.dark = dark


class DistronodeModuleError(distronode.errors.DistronodeError):
    """Sub-class DistronodeError when module failures occur."""
