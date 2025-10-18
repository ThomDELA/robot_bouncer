"""Unit tests for the :mod:`robot_bouncer.services.guard_service` module."""

from __future__ import annotations

from datetime import datetime, timedelta

from robot_bouncer.domain.entities import Guest
from robot_bouncer.domain.exceptions import GuestNotAllowed
from robot_bouncer.services.guard_service import GuardService


class DummyRepository:
    def __init__(self, guest: Guest) -> None:
        self._guest = guest

    def get_by_identifier(self, identifier: str) -> Guest:  # pragma: no cover - trivial
        return self._guest


def test_authorize_returns_guest_when_allowed() -> None:
    guest = Guest(identifier="allowed", name="Allowed", allowed=True)
    service = GuardService(repository=DummyRepository(guest))

    assert service.authorize("allowed") is guest


def test_authorize_raises_when_guest_not_allowed() -> None:
    guest = Guest(
        identifier="denied",
        name="Denied",
        allowed=True,
        allowed_until=datetime.utcnow() - timedelta(minutes=1),
    )
    service = GuardService(repository=DummyRepository(guest))

    try:
        service.authorize("denied")
    except GuestNotAllowed as error:
        assert "not allowed" in str(error)
    else:  # pragma: no cover - defensive
        raise AssertionError("GuardService.authorize should raise GuestNotAllowed")
