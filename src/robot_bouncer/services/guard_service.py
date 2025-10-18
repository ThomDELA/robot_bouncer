"""Application service orchestrating guest access decisions."""

from __future__ import annotations

from datetime import datetime
from typing import Protocol

from robot_bouncer.domain.entities import Guest
from robot_bouncer.domain.exceptions import GuestNotAllowed


class GuestRepository(Protocol):
    """Protocol describing guest persistence operations."""

    def get_by_identifier(self, identifier: str) -> Guest:
        """Retrieve a guest using the unique identifier."""


class GuardService:
    """Service that decides whether a guest may enter."""

    def __init__(self, repository: GuestRepository) -> None:
        self._repository = repository

    def authorize(self, guest_id: str, at: datetime | None = None) -> Guest:
        """Authorize a guest or raise :class:`GuestNotAllowed`."""

        guest = self._repository.get_by_identifier(guest_id)
        if guest.can_enter(at=at):
            return guest
        raise GuestNotAllowed(f"Guest {guest_id!r} is not allowed to enter.")
