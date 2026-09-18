"""Application exceptions for Product Advisor."""

class ProductAdvisorException(Exception):
    """Base exception for all Product Advisor domain errors."""
    def __init__(self, message: str, details: dict = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}


class ServiceUnavailableError(ProductAdvisorException):
    """Raised when an infrastructure service (DB, Search, Storage, Cache, LLM) is unavailable."""
    pass


class ModelUnavailableError(ProductAdvisorException):
    """Raised at startup or runtime when a configured LLM/Vision model is missing."""
    pass


class ConfigurationError(ProductAdvisorException):
    """Raised when critical configuration settings are missing or invalid."""
    pass


class VerificationError(ProductAdvisorException):
    """Raised when an agent verification or constraint validation fails."""
    pass
