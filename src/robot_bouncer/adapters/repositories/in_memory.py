"""In-memory implementation of the guest repository protocol."""

from __future__ import annotations

from typing import Dict

from robot_bouncer.domain.entities import Guest
from robot_bouncer.services.guard_service import GuestRepository


class InMemoryGuestRepository(GuestRepository):
    """Simple dictionary-backed repository for guests."""

    def __init__(self, guests: Dict[str, Guest] | None = None) -> None:
        self._guests: Dict[str, Guest] = guests or {}

    def add(self, guest: Guest) -> None:
        """Persist a guest in memory."""

        self._guests[guest.identifier] = guest

    def get_by_identifier(self, identifier: str) -> Guest:
        """Return a guest by identifier or raise ``KeyError``."""

        return self._guests[identifier]
