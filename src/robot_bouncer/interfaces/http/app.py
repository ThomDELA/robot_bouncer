"""HTTP interface entry point for the robot bouncer service.

This module illustrates where a web framework (FastAPI, Flask, etc.) could be
wired in.  The ``create_app`` function keeps initialization logic encapsulated
so it can be reused across deployment targets and tests.
"""

from __future__ import annotations

from typing import Any

from robot_bouncer.adapters.repositories.in_memory import InMemoryGuestRepository
from robot_bouncer.config.settings import AppSettings, load_settings
from robot_bouncer.domain.entities import Guest
from robot_bouncer.services.guard_service import GuardService


def create_app(settings: AppSettings | None = None) -> dict[str, Any]:
    """Return a framework-agnostic representation of the HTTP app.

    Until a concrete web framework is introduced, we return a dictionary that
    documents the dependencies the HTTP layer is expected to manage.
    """

    app_settings = settings or load_settings()
    repository = InMemoryGuestRepository(
        {
            "demo": Guest(identifier="demo", name="Demo Guest", allowed=True),
        }
    )
    guard_service = GuardService(repository=repository)

    # A real application would initialize framework routes here.  We keep a
    # structured object to make future integration straightforward.
    return {
        "settings": app_settings,
        "repository": repository,
        "services": {"guard": guard_service},
    }
