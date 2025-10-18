"""Minimal HTTP server powering the robot bouncer mini-game."""

from __future__ import annotations

import json
import mimetypes
from dataclasses import dataclass
from datetime import datetime, timedelta
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from random import choice
from typing import Literal
from urllib.parse import urlparse

from robot_bouncer.adapters.repositories.in_memory import InMemoryGuestRepository
from robot_bouncer.config.settings import AppSettings, load_settings
from robot_bouncer.domain.entities import Guest
from robot_bouncer.domain.exceptions import GuestNotAllowed
from robot_bouncer.services.guard_service import GuardService


@dataclass(slots=True)
class AuthorizationResponse:
    """Response returned when the player evaluates a guest."""

    correct: bool
    allowed: bool
    message: str

    def to_dict(self) -> dict[str, object]:
        """Represent the response as a JSON-serialisable dictionary."""

        return {"correct": self.correct, "allowed": self.allowed, "message": self.message}


def _build_demo_guests() -> tuple[InMemoryGuestRepository, dict[str, dict[str, object]]]:
    """Return a populated repository and accompanying scenario metadata."""

    now = datetime.utcnow()
    guests = {
        "vip": Guest(
            identifier="vip",
            name="Val Vega",
            allowed=True,
            allowed_until=now + timedelta(hours=3),
        ),
        "late": Guest(
            identifier="late",
            name="Lina Late",
            allowed=True,
            allowed_until=now - timedelta(minutes=10),
        ),
        "banned": Guest(
            identifier="banned",
            name="Bruno Banned",
            allowed=False,
        ),
        "crew": Guest(
            identifier="crew",
            name="Casey Crew",
            allowed=True,
        ),
    }

    scenarios: dict[str, dict[str, object]] = {
        "vip": {
            "name": "Val Vega",
            "introduction": "An energetic DJ with tonight's headliner badge dangling from their neck.",
            "facts": [
                "Flashes a holographic VIP wristband registered for tonight.",
                "Politely reminds you that they are scheduled to perform in 10 minutes.",
            ],
        },
        "late": {
            "name": "Lina Late",
            "introduction": "A regular who looks nervous while glancing at the countdown clock behind you.",
            "facts": [
                "Presents a pass that expired a few minutes ago.",
                "Insists the robot bouncer always gives five minutes of grace time.",
            ],
        },
        "banned": {
            "name": "Bruno Banned",
            "introduction": "A familiar troublemaker trying their luck with a pair of fake moustaches.",
            "facts": [
                "Banned last week for reprogramming the fog machine into overdrive.",
                "Avoids direct eye contact and keeps glancing at the security cameras.",
            ],
        },
        "crew": {
            "name": "Casey Crew",
            "introduction": "One of the lighting technicians carrying a bundle of neatly coiled cables.",
            "facts": [
                "Shows a permanent crew badge signed by the venue manager.",
                "Mentions they need to swap a spotlight before doors open to the public.",
            ],
        },
    }

    return InMemoryGuestRepository(guests), scenarios


class RobotBouncerWebApp:
    """Simple HTTP application exposing the robot bouncer mini-game."""

    def __init__(self, settings: AppSettings | None = None) -> None:
        self.settings = settings or load_settings()
        self.repository, self.scenarios = _build_demo_guests()
        self.guard_service = GuardService(repository=self.repository)
        self.static_dir = Path(__file__).resolve().parent / "static"
        self.index_file = self.static_dir / "index.html"

    def get_next_guest(self) -> dict[str, object]:
        """Return data describing a random guest scenario."""

        guest_id = choice(list(self.scenarios.keys()))
        metadata = self.scenarios[guest_id]
        return {
            "guestId": guest_id,
            "name": metadata["name"],
            "introduction": metadata["introduction"],
            "facts": metadata["facts"],
        }

    def authorize(self, guest_id: str, action: Literal["allow", "deny"]) -> AuthorizationResponse:
        """Evaluate the player's decision for a given guest."""

        scenario = self.scenarios.get(guest_id)
        if scenario is None:
            raise KeyError(guest_id)

        guest = self.repository.get_by_identifier(guest_id)
        actual_allowed = guest.can_enter(at=datetime.utcnow())

        if action == "allow":
            try:
                self.guard_service.authorize(guest_id, at=datetime.utcnow())
            except GuestNotAllowed:
                return AuthorizationResponse(
                    correct=False,
                    allowed=False,
                    message=f"Oops! {scenario['name']} isn't cleared to enter right now.",
                )
            return AuthorizationResponse(
                correct=True,
                allowed=True,
                message=f"Correct! {scenario['name']} may enter the club.",
            )

        if action == "deny":
            if actual_allowed:
                return AuthorizationResponse(
                    correct=False,
                    allowed=True,
                    message=f"Not quite! {scenario['name']} actually has access tonight.",
                )
            return AuthorizationResponse(
                correct=True,
                allowed=False,
                message=f"Spot on! {scenario['name']} needs to stay outside.",
            )

        raise ValueError(f"Unsupported action: {action}")

    # ---------------------------------------------------------------------
    # HTTP server helpers
    # ---------------------------------------------------------------------
    def _build_handler(self) -> type[BaseHTTPRequestHandler]:
        """Create a request handler bound to the application's state."""

        app = self
        static_dir = self.static_dir
        index_file = self.index_file

        class Handler(BaseHTTPRequestHandler):
            server_version = "RobotBouncerHTTP/1.0"

            def do_GET(self) -> None:  # noqa: N802 - required by BaseHTTPRequestHandler
                parsed = urlparse(self.path)
                if parsed.path == "/":
                    if not index_file.exists():
                        self.send_error(HTTPStatus.INTERNAL_SERVER_ERROR, "Front-end assets are missing.")
                        return
                    self._send_file(index_file)
                    return

                if parsed.path == "/api/next-guest":
                    payload = app.get_next_guest()
                    self._send_json(payload)
                    return

                if parsed.path.startswith("/static/"):
                    relative_path = parsed.path[len("/static/") :]
                    file_path = (static_dir / relative_path).resolve()
                    try:
                        file_path.relative_to(static_dir)
                    except ValueError:
                        self.send_error(HTTPStatus.NOT_FOUND, "File not found.")
                        return
                    if not file_path.exists() or not file_path.is_file():
                        self.send_error(HTTPStatus.NOT_FOUND, "File not found.")
                        return
                    self._send_file(file_path)
                    return

                self.send_error(HTTPStatus.NOT_FOUND, "Not Found")

            def do_POST(self) -> None:  # noqa: N802 - required by BaseHTTPRequestHandler
                parsed = urlparse(self.path)
                if parsed.path != "/api/authorize":
                    self.send_error(HTTPStatus.NOT_FOUND, "Not Found")
                    return

                try:
                    length = int(self.headers.get("Content-Length", "0"))
                except ValueError:
                    self.send_error(HTTPStatus.BAD_REQUEST, "Invalid Content-Length header.")
                    return

                body = self.rfile.read(length) if length else b"{}"

                try:
                    payload = json.loads(body.decode("utf-8"))
                except json.JSONDecodeError:
                    self.send_error(HTTPStatus.BAD_REQUEST, "Invalid JSON payload.")
                    return

                guest_id = payload.get("guest_id")
                action = payload.get("action")

                if not isinstance(guest_id, str) or action not in {"allow", "deny"}:
                    self.send_error(HTTPStatus.BAD_REQUEST, "Payload must include 'guest_id' and 'action'.")
                    return

                try:
                    result = app.authorize(guest_id, action)
                except KeyError:
                    self.send_error(HTTPStatus.NOT_FOUND, "Guest not recognised by the mini-game.")
                    return

                self._send_json(result.to_dict())

            # ------------------------------------------------------------------
            # Helper methods
            # ------------------------------------------------------------------
            def _send_json(self, payload: dict[str, object]) -> None:
                body = json.dumps(payload).encode("utf-8")
                self.send_response(HTTPStatus.OK)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            def _send_file(self, path: Path) -> None:
                if path.suffix:
                    mimetype, _ = mimetypes.guess_type(path.name)
                else:
                    mimetype = "application/octet-stream"
                if mimetype and mimetype.startswith("text/"):
                    content_type = f"{mimetype}; charset=utf-8"
                else:
                    content_type = mimetype or "application/octet-stream"

                data = path.read_bytes()
                self.send_response(HTTPStatus.OK)
                self.send_header("Content-Type", content_type)
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)

            def log_message(self, format: str, *args: object) -> None:  # noqa: A003 - matches BaseHTTPRequestHandler signature
                """Silence default logging to keep the console tidy during tests."""

                return

        return Handler

    def serve(self, host: str = "127.0.0.1", port: int = 8000) -> None:
        """Start a blocking HTTP server for local play."""

        handler = self._build_handler()
        with ThreadingHTTPServer((host, port), handler) as httpd:
            try:
                httpd.serve_forever()
            except KeyboardInterrupt:  # pragma: no cover - manual shutdown
                pass


def create_app(settings: AppSettings | None = None) -> RobotBouncerWebApp:
    """Factory returning the configured web application."""

    return RobotBouncerWebApp(settings=settings)


__all__ = ["AuthorizationResponse", "RobotBouncerWebApp", "create_app"]


if __name__ == "__main__":  # pragma: no cover - manual entry point
    create_app().serve()
