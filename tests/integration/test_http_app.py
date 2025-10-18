import pytest

from robot_bouncer.interfaces.http.app import AuthorizationResponse, create_app


def test_next_guest_returns_minimal_payload():
    app = create_app()

    payload = app.get_next_guest()

    assert set(payload) == {"guestId", "name", "introduction", "facts"}
    assert isinstance(payload["facts"], list)
    assert payload["facts"]


def test_authorize_allows_valid_guest():
    app = create_app()

    result = app.authorize("vip", "allow")

    assert isinstance(result, AuthorizationResponse)
    assert result.allowed is True
    assert result.correct is True


def test_authorize_handles_denied_guests():
    app = create_app()

    result = app.authorize("banned", "deny")

    assert result.allowed is False
    assert result.correct is True


def test_authorize_identifies_incorrect_choice():
    app = create_app()

    result = app.authorize("crew", "deny")

    assert result.allowed is True
    assert result.correct is False


def test_unknown_guest_raises_key_error():
    app = create_app()

    with pytest.raises(KeyError):
        app.authorize("unknown", "allow")
