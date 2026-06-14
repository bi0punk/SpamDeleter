import imaplib
import base64


def connect(config: "Config") -> imaplib.IMAP4_SSL:
    if config.oauth2_enabled:
        return _connect_oauth2(config)
    return _connect_password(config)


def _connect_password(config: "Config") -> imaplib.IMAP4_SSL:
    mail = imaplib.IMAP4_SSL(config.imap_host, config.imap_port)
    mail.login(config.email, config.password)
    return mail


def _connect_oauth2(config: "Config") -> imaplib.IMAP4_SSL:
    token = _get_oauth2_token(config)
    mail = imaplib.IMAP4_SSL(config.imap_host, config.imap_port)
    auth_string = f"user={config.email}\x01auth=Bearer {token}\x01\x01"
    mail.authenticate("XOAUTH2", lambda _: base64.b64encode(auth_string.encode()).decode())
    return mail


def _get_oauth2_token(config: "Config") -> str:
    prov = config.oauth2_provider.lower()

    if prov == "google":
        return _google_refresh_token(config)
    elif prov == "microsoft":
        return _microsoft_refresh_token(config)
    else:
        raise ValueError(f"OAuth2 provider '{prov}' no soportado. Usa 'google' o 'microsoft'.")


def _google_refresh_token(config: "Config") -> str:
    try:
        from google.oauth2.credentials import Credentials
        from google.auth.transport.requests import Request
    except ImportError:
        raise SystemExit("google-auth-oauthlib requerido para OAuth2 con Google. pip install google-auth-oauthlib")

    creds = Credentials(
        token=None,
        refresh_token=config.oauth2_refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=config.oauth2_client_id,
        client_secret=config.oauth2_client_secret,
        scopes=["https://mail.google.com/"],
    )
    creds.refresh(Request())
    return creds.token


def _microsoft_refresh_token(config: "Config") -> str:
    try:
        import msal
    except ImportError:
        raise SystemExit("msal requerido para OAuth2 con Microsoft. pip install msal")

    app = msal.ConfidentialClientApplication(
        config.oauth2_client_id,
        authority="https://login.microsoftonline.com/common",
        client_credential=config.oauth2_client_secret,
    )
    result = app.acquire_token_by_refresh_token(
        config.oauth2_refresh_token,
        scopes=["https://outlook.office.com/IMAP.AccessAsUser.All"],
    )
    if "access_token" not in result:
        raise RuntimeError(f"Error obteniendo token Microsoft: {result.get('error_description', result)}")
    return result["access_token"]
