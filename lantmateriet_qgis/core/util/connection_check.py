from qgis.core import QgsBlockingNetworkRequest
from qgis.PyQt.QtCore import QUrl
from qgis.PyQt.QtNetwork import QNetworkRequest

from lantmateriet_qgis.core.util.oauth_config import fetch_access_token
from lantmateriet_qgis.core.util.subscriptions import status_means_no_access


def has_no_access(url: str, authcfg: str) -> bool:
    """Whether the service at ``url`` rejects the given authentication.

    Each service is tested on its own, since an organisation may use different
    system accounts for different services. Returns False when the answer is
    unclear, for example when the token or the service cannot be reached.

    The token is requested directly instead of through QGIS' authentication
    handling, which retries a rejected request for many seconds before giving up.
    """
    try:
        token = fetch_access_token(authcfg)
    except RuntimeError:
        return False
    request = QNetworkRequest(QUrl(url))
    request.setRawHeader(b"Accept", b"application/json, application/geo+json")
    request.setRawHeader(b"Authorization", f"Bearer {token}".encode())
    blocking = QgsBlockingNetworkRequest()
    blocking.get(request)
    status = blocking.reply().attribute(
        QNetworkRequest.Attribute.HttpStatusCodeAttribute
    )
    return status_means_no_access(status if isinstance(status, int) else None)
