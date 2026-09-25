"""
Tests for reading OAuth2 auth configurations.

These cover the shapes a stored oauth2config can actually have: written by
QGIS itself, written by this plugin's own dialog (only a handful of keys), or
missing/unreadable entirely.
"""

import uuid

from qgis.core import QgsAuthMethodConfig

from lantmateriet_qgis.core.util.oauth_config import (
    get_scopes,
    load_oauth_config,
)


class TestGetScopes:
    """Tests for get_scopes()."""

    def test_returns_scopes_of_a_normal_config(self):
        assert get_scopes({"scope": "a b c"}) == ["a", "b", "c"]

    def test_missing_key_returns_empty_list(self):
        """Configurations created by dlg_access don't contain a scope key."""
        assert get_scopes({}) == []

    def test_null_value_returns_empty_list(self):
        """QGIS serializes an unset scope as JSON null, not as an empty string.

        Regression test: config.get("scope", "") returned None for these, and
        the subsequent .split(" ") raised AttributeError while applying the
        options page.
        """
        assert get_scopes({"scope": None}) == []

    def test_empty_string_returns_empty_list(self):
        """An empty scope must not yield a list containing an empty scope.

        Otherwise it is joined back in as a leading space when scopes are added.
        """
        assert get_scopes({"scope": ""}) == []

    def test_surrounding_whitespace_is_dropped(self):
        assert get_scopes({"scope": " a  b "}) == ["a", "b"]


class TestLoadOAuthConfig:
    """Tests for load_oauth_config()."""

    def test_loads_a_stored_config(self, auth_config_builder):
        config_id = auth_config_builder("https://example.com/token")
        config = load_oauth_config(config_id)
        assert config["tokenUrl"] == "https://example.com/token"

    def test_null_scope_is_preserved_as_none(self, auth_config_builder):
        config_id = auth_config_builder("https://example.com/token", scope=None)
        config = load_oauth_config(config_id)
        assert config["scope"] is None
        assert get_scopes(config) == []

    def test_unknown_config_id_returns_empty_config(self, qgis_auth_manager):
        """A stale auth config id must not raise while reading."""
        assert load_oauth_config(str(uuid.uuid4())[:7]) == {}

    def test_non_oauth2_config_returns_empty_config(self, qgis_auth_manager):
        """A Basic auth config has no oauth2config key in its config map."""
        config = QgsAuthMethodConfig()
        config.setName("test_basic")
        config.setMethod("Basic")
        config.setConfigMap({"username": "user", "password": "pass"})
        qgis_auth_manager.storeAuthenticationConfig(config)
        qgis_auth_manager.updateConfigAuthMethods()

        try:
            assert load_oauth_config(config.id()) == {}
        finally:
            qgis_auth_manager.removeAuthenticationConfig(config.id())

    def test_unparseable_payload_returns_empty_config(self, qgis_auth_manager):
        config = QgsAuthMethodConfig()
        config.setName("test_broken_oauth2")
        config.setMethod("OAuth2")
        config.setConfigMap({"oauth2config": "not json"})
        qgis_auth_manager.storeAuthenticationConfig(config)
        qgis_auth_manager.updateConfigAuthMethods()

        try:
            assert load_oauth_config(config.id()) == {}
        finally:
            qgis_auth_manager.removeAuthenticationConfig(config.id())
