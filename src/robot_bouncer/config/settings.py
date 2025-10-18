"""Application configuration objects and utilities.

This module centralizes project settings to keep configuration management
consistent across entry points and services.  The default ``AppSettings``
class can be expanded with strongly-typed attributes as the project evolves.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass(slots=True)
class AppSettings:
    """Container for application configuration values.

    Attributes
    ----------
    environment:
        Name of the current runtime environment (for example, ``"dev"`` or
        ``"prod"``).
    debug:
        Boolean flag controlling verbose logging or other development-only
        features.
    metadata:
        Arbitrary metadata describing the service.  This can be populated from
        configuration files, environment variables, or secret stores.
    """

    environment: str = "dev"
    debug: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


def load_settings(**overrides: Any) -> AppSettings:
    """Create an :class:`AppSettings` instance.

    Parameters
    ----------
    **overrides:
        Keyword arguments used to override the default attribute values.

    Returns
    -------
    AppSettings
        The configured settings object.
    """

    settings = AppSettings()
    for key, value in overrides.items():
        if hasattr(settings, key):
            setattr(settings, key, value)
    return settings
