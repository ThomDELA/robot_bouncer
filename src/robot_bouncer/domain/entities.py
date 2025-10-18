"""Domain entities representing the core business concepts.

The domain layer should remain free of infrastructure concerns.  The
``Guest`` entity is an example placeholder that can be extended with richer
attributes and validation logic as requirements emerge.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(slots=True)
class Guest:
    """Representation of a person interacting with the robot bouncer."""

    identifier: str
    name: str
    allowed: bool
    allowed_until: Optional[datetime] = None

    def can_enter(self, at: Optional[datetime] = None) -> bool:
        """Return ``True`` when the guest is currently allowed to enter."""

        check_time = at or datetime.utcnow()
        if not self.allowed:
            return False
        if self.allowed_until and check_time > self.allowed_until:
            return False
        return True
