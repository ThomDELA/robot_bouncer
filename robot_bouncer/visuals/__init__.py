"""Rendering backends for Robot Bouncer."""
from .base import GameRenderer
from .console import ConsoleRenderer

__all__ = ["GameRenderer", "ConsoleRenderer"]
