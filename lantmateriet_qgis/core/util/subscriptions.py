"""Helpers for detecting APIs the application is not subscribed to.

The Lantmäteriet token endpoint silently replaces scopes the application is not
subscribed to with ``default``. Comparing the requested scopes with the scopes in
the token response therefore reveals missing API subscriptions.
"""

import json


def parse_granted_scopes(body: bytes | str) -> set[str]:
    """Return the scopes of a token endpoint response, empty if unreadable."""
    try:
        data = json.loads(body)
    except (TypeError, ValueError):
        return set()
    if not isinstance(data, dict):
        return set()
    scope = data.get("scope")
    if not isinstance(scope, str):
        return set()
    return {part for part in scope.split(" ") if part}


def find_missing_subscriptions(
    requested: dict[str, str], granted: set[str]
) -> list[str]:
    """Return the names of the services whose scope was not granted.

    :param requested: Mapping from service name to the scope it requires.
    :param granted: Scopes found in the token response.
    """
    return [name for name, scope in requested.items() if scope not in granted]
