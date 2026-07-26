"""
Tests for Settings.validate() QGIS-dependent behavior.

These tests validate that the settings validation correctly checks OAuth2 auth
configs against expected token/authorize URLs for Lantmäteriet services.
"""

import pytest
from qgis.core import QgsAuthMethodConfig

from lantmateriet_qgis.config import URLConfig
from lantmateriet_qgis.core.settings import Settings
from lantmateriet_qgis.core.util.oauth_config import GrantFlow


class TestSettingsValidateNgp:
    """Tests for Settings.validate() on the NGP (Nationella geodataplattformen) service."""

    def test_ngp_disabled_returns_no_errors(self, qgis_auth_manager):
        """When ngp_enabled=False, validate() should not check anything."""
        settings = Settings(ngp_enabled=False, ngp="production")
        errors = settings.validate()
        assert errors == []

    def test_ngp_custom_url_valid_returns_no_errors(self, qgis_auth_manager):
        """Custom URL that is valid should not produce errors."""
        settings = Settings(
            ngp_enabled=True,
            ngp="https://example.com/api",
        )
        errors = settings.validate()
        assert errors == []

    def test_ngp_custom_url_invalid_returns_error(self, qgis_auth_manager):
        """Custom URL that is not a valid URL should produce an error."""
        settings = Settings(
            ngp_enabled=True,
            ngp="not a valid url",
        )
        errors = settings.validate()
        assert len(errors) == 1
        assert "Egen URL för Nationella geodataplattformen är inte giltig" in errors[0]

    def test_ngp_production_missing_authcfg_returns_error(self, qgis_auth_manager):
        """Production endpoint with no auth config should produce an error."""
        settings = Settings(
            ngp_enabled=True,
            ngp="production",
            ngp_authcfg="",
        )
        errors = settings.validate()
        assert len(errors) >= 1
        assert any(
            "Autentisering för Nationella geodataplattformen saknas" in e
            for e in errors
        )

    def test_ngp_production_nonexistent_authcfg_returns_error(self, qgis_auth_manager):
        """Production endpoint with a non-existent auth config ID should produce an error."""
        settings = Settings(
            ngp_enabled=True,
            ngp="production",
            ngp_authcfg="nonexistent_id",
        )
        errors = settings.validate()
        assert len(errors) >= 1
        assert any(
            "Autentisering för Nationella geodataplattformen saknas" in e
            for e in errors
        )

    def test_ngp_production_non_oauth2_authcfg_returns_error(
        self, qgis_auth_manager
    ):
        """Production endpoint with a non-OAuth2 auth config should produce an error."""
        auth_mgr = qgis_auth_manager
        config = QgsAuthMethodConfig()
        config.setId("basic_auth_id")
        config.setName("Basic Auth (not OAuth2)")
        config.setMethod("Basic")
        auth_mgr.storeAuthenticationConfig(config)
        auth_mgr.updateConfigAuthMethods()

        try:
            settings = Settings(
                ngp_enabled=True,
                ngp="production",
                ngp_authcfg="basic_auth_id",
            )
            errors = settings.validate()
            assert len(errors) >= 1
            assert any(
                "Autentisering för Nationella geodataplattformen är inte giltig" in e
                for e in errors
            )
        finally:
            auth_mgr.removeAuthConfig("basic_auth_id")

    def test_ngp_production_oauth2_wrong_token_url_returns_error(
        self, auth_config_builder, qgis_auth_manager
    ):
        """Production OAuth2 with wrong token URL should produce an error."""
        authcfg = auth_config_builder(
            token_url="https://wrong-server.com/token",
            request_url=URLConfig.LM_PROD_AUTH_URL + "authorize",
        )

        settings = Settings(
            ngp_enabled=True,
            ngp="production",
            ngp_authcfg=authcfg,
        )
        errors = settings.validate()
        assert len(errors) >= 1
        assert any("Token URL för Nationella geodataplattformen är inte giltig" in e
                   for e in errors)

    def test_ngp_production_oauth2_auth_code_wrong_authorize_url_returns_error(
        self, auth_config_builder
    ):
        """Production OAuth2 with AUTH_CODE grant but wrong authorize URL."""
        authcfg = auth_config_builder(
            token_url=URLConfig.LM_PROD_AUTH_URL + "token",
            request_url="https://wrong-server.com/authorize",
            grant_flow=GrantFlow.AUTH_CODE,
        )

        settings = Settings(
            ngp_enabled=True,
            ngp="production",
            ngp_authcfg=authcfg,
        )
        errors = settings.validate()
        assert len(errors) >= 1
        assert any("Token URL för Nationella geodataplattformen är inte giltig" in e
                   for e in errors)

    def test_ngp_production_oauth2_valid_config_returns_no_errors(
        self, auth_config_builder
    ):
        """Production OAuth2 with correct token/authorize URLs should validate."""
        authcfg = auth_config_builder(
            token_url=URLConfig.LM_PROD_AUTH_URL + "token",
            request_url=URLConfig.LM_PROD_AUTH_URL + "authorize",
            grant_flow=GrantFlow.AUTH_CODE,
        )

        settings = Settings(
            ngp_enabled=True,
            ngp="production",
            ngp_authcfg=authcfg,
        )
        errors = settings.validate()
        assert errors == []

    def test_ngp_verification_oauth2_valid_config_returns_no_errors(
        self, auth_config_builder
    ):
        """Verification OAuth2 with correct token/authorize URLs should validate."""
        authcfg = auth_config_builder(
            token_url=URLConfig.LM_VER_AUTH_URL + "token",
            request_url=URLConfig.LM_VER_AUTH_URL + "authorize",
            grant_flow=GrantFlow.AUTH_CODE_PKCE,
        )

        settings = Settings(
            ngp_enabled=True,
            ngp="verification",
            ngp_authcfg=authcfg,
        )
        errors = settings.validate()
        assert errors == []


class TestSettingsValidateOvrig:
    """Tests for Settings.validate() on the Övriga tjänster (other services)."""

    def test_ovrig_disabled_returns_no_errors(self, qgis_auth_manager):
        """When ovrig_enabled=False, validate() should not check anything."""
        settings = Settings(ovrig_enabled=False, ovrig="production")
        errors = settings.validate()
        assert errors == []

    def test_ovrig_custom_url_valid_returns_no_errors(self, qgis_auth_manager):
        """Custom URL that is valid should not produce errors."""
        settings = Settings(
            ovrig_enabled=True,
            ovrig="https://example.com/api",
        )
        errors = settings.validate()
        assert errors == []

    def test_ovrig_custom_url_invalid_returns_error(self, qgis_auth_manager):
        """Custom URL that is not a valid URL should produce an error."""
        settings = Settings(
            ovrig_enabled=True,
            ovrig="not a valid url",
        )
        errors = settings.validate()
        assert len(errors) == 1
        assert "Egen URL för Övriga tjänster är inte giltig" in errors[0]

    def test_ovrig_production_missing_authcfg_returns_error(self, qgis_auth_manager):
        """Production endpoint with no auth config should produce an error."""
        settings = Settings(
            ovrig_enabled=True,
            ovrig="production",
            ovrig_authcfg="",
        )
        errors = settings.validate()
        assert len(errors) >= 1
        assert any("Autentisering för Övriga tjänster saknas" in e for e in errors)

    def test_ovrig_production_oauth2_valid_config_returns_no_errors(
        self, auth_config_builder
    ):
        """Production OAuth2 with correct token/authorize URLs should validate."""
        authcfg = auth_config_builder(
            token_url=URLConfig.LM_PROD_AUTH_URL + "token",
            request_url=URLConfig.LM_PROD_AUTH_URL + "authorize",
            grant_flow=GrantFlow.AUTH_CODE_PKCE,
        )

        settings = Settings(
            ovrig_enabled=True,
            ovrig="production",
            ovrig_authcfg=authcfg,
        )
        errors = settings.validate()
        assert errors == []


class TestSettingsValidateBoth:
    """Tests for Settings.validate() with both services enabled."""

    def test_both_services_valid_returns_no_errors(self, auth_config_builder):
        """Both NGP and Övriga with correct configs should validate."""
        ngp_authcfg = auth_config_builder(
            token_url=URLConfig.LM_PROD_AUTH_URL + "token",
            request_url=URLConfig.LM_PROD_AUTH_URL + "authorize",
        )
        ovrig_authcfg = auth_config_builder(
            token_url=URLConfig.LM_PROD_AUTH_URL + "token",
            request_url=URLConfig.LM_PROD_AUTH_URL + "authorize",
        )

        settings = Settings(
            ngp_enabled=True,
            ngp="production",
            ngp_authcfg=ngp_authcfg,
            ovrig_enabled=True,
            ovrig="production",
            ovrig_authcfg=ovrig_authcfg,
        )
        errors = settings.validate()
        assert errors == []

    def test_ngp_valid_ovrig_invalid_returns_one_error(self, auth_config_builder):
        """One valid service + one invalid should return the invalid error."""
        ngp_authcfg = auth_config_builder(
            token_url=URLConfig.LM_PROD_AUTH_URL + "token",
            request_url=URLConfig.LM_PROD_AUTH_URL + "authorize",
        )

        settings = Settings(
            ngp_enabled=True,
            ngp="production",
            ngp_authcfg=ngp_authcfg,
            ovrig_enabled=True,
            ovrig="not a valid url",
        )
        errors = settings.validate()
        assert len(errors) >= 1
        assert any("Övriga tjänster är inte giltig" in e for e in errors)
        assert not any("Nationella" in e for e in errors)
