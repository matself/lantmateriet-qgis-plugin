"""Tests for detecting missing API subscriptions from a token response."""

import json

from lantmateriet_qgis.core.util.subscriptions import (
    find_missing_subscriptions,
    parse_granted_scopes,
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
