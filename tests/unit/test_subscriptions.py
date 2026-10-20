"""Tests for detecting missing API subscriptions from a token response."""

import json

from lantmateriet_qgis.core.util.subscriptions import (
    find_missing_subscriptions,
    parse_granted_scopes,
    status_means_no_access,
)


class TestParseGrantedScopes:
    def test_returns_scopes_of_a_token_response(self):
        body = json.dumps({"scope": "a b", "token_type": "Bearer"})
        assert parse_granted_scopes(body) == {"a", "b"}

    def test_accepts_bytes(self):
        assert parse_granted_scopes(b'{"scope": "default"}') == {"default"}

    def test_missing_scope_key_returns_empty_set(self):
        assert parse_granted_scopes('{"token_type": "Bearer"}') == set()

    def test_null_scope_returns_empty_set(self):
        assert parse_granted_scopes('{"scope": null}') == set()

    def test_invalid_json_returns_empty_set(self):
        assert parse_granted_scopes("not json") == set()

    def test_non_object_json_returns_empty_set(self):
        assert parse_granted_scopes("[1, 2]") == set()


class TestFindMissingSubscriptions:
    def test_all_granted_returns_empty_list(self):
        requested = {"Adress": "adr_read", "Register": "reg_read"}
        assert find_missing_subscriptions(requested, {"adr_read", "reg_read"}) == []

    def test_scopes_replaced_by_default_are_reported(self):
        requested = {"Adress": "adr_read", "Register": "reg_read"}
        assert find_missing_subscriptions(requested, {"adr_read"}) == ["Register"]

    def test_only_default_granted_reports_everything(self):
        requested = {"Adress": "adr_read", "Register": "reg_read"}
        assert find_missing_subscriptions(requested, {"default"}) == [
            "Adress",
            "Register",
        ]

    def test_nothing_requested_returns_empty_list(self):
        assert find_missing_subscriptions({}, {"default"}) == []


class TestStatusMeansNoAccess:
    def test_unauthorized_and_forbidden_mean_no_access(self):
        assert status_means_no_access(401)
        assert status_means_no_access(403)

    def test_success_does_not_mean_no_access(self):
        assert not status_means_no_access(200)

    def test_rate_limit_and_server_errors_say_nothing(self):
        assert not status_means_no_access(429)
        assert not status_means_no_access(500)
        assert not status_means_no_access(503)

    def test_missing_status_says_nothing(self):
        """No response (network error, timeout) must not hide a service."""
        assert not status_means_no_access(None)
