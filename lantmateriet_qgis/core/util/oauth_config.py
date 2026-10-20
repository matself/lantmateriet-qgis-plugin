import base64
import json
from typing import Any, TypedDict

from qgis.core import (
    QgsApplication,
    QgsAuthManager,
    QgsAuthMethodConfig,
    QgsBlockingNetworkRequest,
)
from qgis.PyQt.QtCore import QByteArray, QUrl, QUrlQuery
from qgis.PyQt.QtNetwork import QNetworkRequest

from lantmateriet_qgis.core.util.subscriptions import parse_granted_scopes


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


def _request_token(authcfg: str, scopes: list[str]) -> bytes:
    """Request a token with client credentials and return the raw response body.

    Only client credentials configurations are supported. Raises RuntimeError if
    the token endpoint cannot be reached or rejects the credentials.
    """
    config = load_oauth_config(authcfg)
    token_url = config.get("tokenUrl")
    client_id = config.get("clientId")
    client_secret = config.get("clientSecret")
    if not (token_url and client_id and client_secret):
        raise RuntimeError("The authentication has no token URL or credentials")

    request = QNetworkRequest(QUrl(token_url))
    request.setHeader(
        QNetworkRequest.KnownHeaders.ContentTypeHeader,
        "application/x-www-form-urlencoded",
    )
    credentials = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
    request.setRawHeader(b"Authorization", f"Basic {credentials}".encode())

    form = QUrlQuery()
    form.addQueryItem("grant_type", "client_credentials")
    if scopes:
        form.addQueryItem("scope", " ".join(scopes))
    body = QByteArray(
        form.toString(QUrl.ComponentFormattingOption.FullyEncoded).encode()
    )

    blocking = QgsBlockingNetworkRequest()
    error = blocking.post(request, body)
    if error != QgsBlockingNetworkRequest.ErrorCode.NoError:
        raise RuntimeError(blocking.errorMessage())
    return bytes(blocking.reply().content())


def fetch_granted_scopes(authcfg: str, scopes: list[str]) -> set[str]:
    """Request a token for the given scopes and return the scopes actually granted."""
    return parse_granted_scopes(_request_token(authcfg, scopes))


def fetch_access_token(authcfg: str) -> str:
    """Request a token and return the access token. Raises RuntimeError on failure."""
    try:
        token = json.loads(_request_token(authcfg, [])).get("access_token")
    except ValueError as e:
        raise RuntimeError("Unreadable token response") from e
    if not isinstance(token, str) or not token:
        raise RuntimeError("No access token in the token response")
    return token
