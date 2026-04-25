class AgentsShipgateError(Exception):
    """Base exception for expected Agents Shipgate failures."""


class ConfigError(AgentsShipgateError):
    """Raised when the manifest is missing or invalid."""


class InputParseError(AgentsShipgateError):
    """Raised when a declared input source cannot be parsed."""

