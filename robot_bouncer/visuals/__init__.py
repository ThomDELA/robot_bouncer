"""Rendering backends for Robot Bouncer."""
from .base import GameRenderer
from .console import ConsoleRenderer
from .grid import InteractiveBoard

__all__ = ["GameRenderer", "ConsoleRenderer", "InteractiveBoard"]
