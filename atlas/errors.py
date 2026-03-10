"""Custom exceptions for ATLAS with structured error handling."""

from typing import Any


class AtlasError(Exception):
    """Base exception for all ATLAS errors."""

    def __init__(self, message: str, details: dict[str, Any] | None = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}

    def __str__(self) -> str:
        if self.details:
            return f"{self.message} | details={self.details}"
        return self.message


class ServiceError(AtlasError):
    """External service call failed (Google, OpenAI, Tavily)."""

    def __init__(self, service: str, operation: str, cause: Exception | None = None):
        details = {"service": service, "operation": operation}
        if cause:
            details["cause"] = f"{type(cause).__name__}: {cause}"
        super().__init__(f"{service} {operation} failed", details)
        self.__cause__ = cause


class GoogleServiceError(ServiceError):
    """Google API error (Calendar, Gmail)."""

    def __init__(self, operation: str, cause: Exception | None = None):
        super().__init__("Google", operation, cause)


class OpenAIServiceError(ServiceError):
    """OpenAI API error."""

    def __init__(self, operation: str, cause: Exception | None = None):
        super().__init__("OpenAI", operation, cause)


class VaultError(AtlasError):
    """Obsidian vault operation failed."""

    def __init__(self, operation: str, path: str | None = None, cause: Exception | None = None):
        details = {"operation": operation}
        if path:
            details["path"] = path
        if cause:
            details["cause"] = f"{type(cause).__name__}: {cause}"
        super().__init__(f"Vault {operation} failed", details)
        self.__cause__ = cause


class MemoryError(AtlasError):
    """Memory/embedding operation failed."""

    def __init__(self, operation: str, cause: Exception | None = None):
        details = {"operation": operation}
        if cause:
            details["cause"] = f"{type(cause).__name__}: {cause}"
        super().__init__(f"Memory {operation} failed", details)
        self.__cause__ = cause
