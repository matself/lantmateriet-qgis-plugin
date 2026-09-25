import json
from typing import Any, TypedDict

from qgis.core import QgsApplication, QgsAuthManager, QgsAuthMethodConfig


class GrantFlow:
    AUTH_CODE = 0
    IMPLICIT = 1
    RESOURCE_OWNER = 2
    AUTH_CODE_PKCE = 3
    CLIENT_CREDENTIALS = 4


class OAuth2ConfigData(TypedDict, total=False):
    """The oauth2config payload of a QGIS OAuth2 auth configuration.

    Every key is optional: configurations written by this plugin only contain a
    handful of keys, and QGIS itself may serialize unset string properties as
    JSON null. Always read values with ``.get()`` and treat null as unset.
    """

    accessMethod: int
    apiKey: str
    clientId: str
    clientSecret: str
    configType: int
    customHeader: str
    extraTokens: dict[str, Any]
    description: str
    grantFlow: int
    id: str
    name: str
    objectName: str
    password: str
    persistToken: bool
    queryPairs: dict[str, Any]
    redirectHost: str
    redirectPort: int
    redirectUrl: str
    refreshTokenUrl: str
    requestTimeout: int
    requestUrl: str
    scope: str
    tokenUrl: str
    username: str
    version: int


def load_oauth_config(authcfg: str) -> OAuth2ConfigData:
    auth_manager: QgsAuthManager = QgsApplication.authManager()
    config = QgsAuthMethodConfig()
    auth_manager.loadAuthenticationConfig(authcfg, config, True)
    raw = config.config("oauth2config")
    if not raw:
        # Unknown config id, non-OAuth2 method, or locked auth database
        return OAuth2ConfigData()
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return OAuth2ConfigData()
    return OAuth2ConfigData(**data)


def get_scopes(config: OAuth2ConfigData) -> list[str]:
    """Return the scopes of an OAuth2 configuration as a list.

    The scope key may be absent (configurations created by this plugin only set
    a handful of keys) or present but null (QGIS serializes unset string
    properties as JSON null), so neither indexing nor a get() default suffices.
    """
    return [scope for scope in (config.get("scope") or "").split(" ") if scope]


def store_oauth_config(authcfg: str, data: OAuth2ConfigData):
    auth_manager: QgsAuthManager = QgsApplication.authManager()
    config = QgsAuthMethodConfig()
    auth_manager.loadAuthenticationConfig(authcfg, config, True)
    config.setConfigMap(
        dict(
            oauth2config=json.dumps(data),
        )
    )
    auth_manager.storeAuthenticationConfig(config, overwrite=True)
    auth_manager.updateConfigAuthMethods()
