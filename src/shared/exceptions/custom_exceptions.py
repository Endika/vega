class VegaException(Exception):
    """Base exception for Vega application."""


class ValidationError(VegaException):
    """Validation error."""


class NotFoundError(VegaException):
    """Resource not found error."""


class BusinessLogicError(VegaException):
    """Business logic error."""


class ExternalServiceError(VegaException):
    """External service error."""


class DatabaseError(VegaException):
    """Database error."""


class WebSocketError(VegaException):
    """WebSocket error."""
