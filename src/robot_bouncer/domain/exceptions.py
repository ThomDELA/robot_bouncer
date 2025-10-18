"""Domain-specific exception hierarchy."""


class DomainError(Exception):
    """Base error for domain-level issues."""


class GuestNotAllowed(DomainError):
    """Raised when a guest is denied access."""
