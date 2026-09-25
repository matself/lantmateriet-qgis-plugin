"""
Pytest fixtures for QGIS-dependent tests.

Boots a headless QgsApplication once per test session and provides fixtures
for auth manager setup.
"""

import json
import uuid

import pytest
from qgis.core import (
    QgsApplication,
    QgsAuthManager,
    QgsAuthMethodConfig,
)
from qgis.testing import start_app

from lantmateriet_qgis.core.util.oauth_config import GrantFlow


@pytest.fixture(scope="session")
def qgis_app():
    """Start a headless QGIS application for the test session.

    Returns the QgsApplication instance. Tests should not call this directly;
    use the dependent fixtures instead (e.g., qgis_auth_manager).
    """
    app = start_app()
    yield app


@pytest.fixture(scope="session")
def qgis_auth_manager(qgis_app):
    """Get the QGIS auth manager, with a temporary master password set.

    The master password is set to a throwaway value so auth config operations
    don't prompt for user input during tests. The auth database is created
    in a temporary location and cleaned up after the session.
    """
    auth_mgr = QgsApplication.authManager()

    master_pass = "test_master_password_12345"
    auth_mgr.setMasterPassword(master_pass, True)

    yield auth_mgr


_UNSET = object()


def _create_oauth2_config(
    auth_manager: QgsAuthManager,
    token_url: str,
    request_url: str = "",
    grant_flow: int = GrantFlow.AUTH_CODE_PKCE,
    name: str = "",
    scope=_UNSET,
) -> str:
    """Create a test OAuth2 auth config and return its ID.

    Args:
        auth_manager: QgsAuthManager instance
        token_url: Token endpoint URL
        request_url: Authorization endpoint URL (only needed for AUTH_CODE* flows)
        grant_flow: One of GrantFlow constants
        name: Config name (auto-generated if not provided)
        scope: Scope value to store. Pass None to store an explicit JSON null,
            or the sentinel default to leave the key out entirely - both occur
            in the wild and neither is a string.

    Returns:
        The auth config ID (unique string)
    """
    config_id = str(uuid.uuid4())
    name = name or f"test_oauth2_{config_id[:8]}"

    oauth2_data = {
        "accessMethod": 1,
        "apiKey": "",
        "clientId": "test_client_id",
        "clientSecret": "test_client_secret",
        "configType": 1,
        "customHeader": "",
        "description": f"Test OAuth2 config",
        "extraTokens": {},
        "grantFlow": grant_flow,
        "id": config_id,
        "name": name,
        "objectName": "QgsAuthOAuth2Config",
        "password": "",
        "persistToken": False,
        "queryPairs": {},
        "redirectHost": "localhost",
        "redirectPort": 7071,
        "redirectUrl": "http://localhost:7071/",
        "refreshTokenUrl": "",
        "requestTimeout": 30,
        "requestUrl": request_url,
        "scope": "openid profile email",
        "tokenUrl": token_url,
        "username": "",
        "version": 2,
    }

    if scope is _UNSET:
        del oauth2_data["scope"]
    else:
        oauth2_data["scope"] = scope

    config = QgsAuthMethodConfig()
    config.setId(config_id)
    config.setName(name)
    config.setMethod("OAuth2")
    config.setConfigMap(dict(oauth2config=json.dumps(oauth2_data)))

    auth_manager.storeAuthenticationConfig(config)
    auth_manager.updateConfigAuthMethods()

    return config_id


@pytest.fixture
def auth_config_builder(qgis_auth_manager):
    """Fixture providing a helper to create test OAuth2 configs.

    Automatically tracks and cleans up configs created during the test.
    """
    auth_mgr = qgis_auth_manager
    created_ids = []

    def builder(
        token_url: str,
        request_url: str = "",
        grant_flow: int = GrantFlow.AUTH_CODE_PKCE,
        name: str = "",
        scope="openid profile email",
    ) -> str:
        """Create and return an OAuth2 config ID."""
        config_id = _create_oauth2_config(
            auth_mgr, token_url, request_url, grant_flow, name, scope
        )
        created_ids.append(config_id)
        return config_id

    yield builder

    # Clean up created configs after the test
    for config_id in created_ids:
        auth_mgr.removeAuthenticationConfig(config_id)
