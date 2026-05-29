import os
import argparse
from dataclasses import dataclass, field
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

PROVIDERS = {
    "gmail": {"host": "imap.gmail.com", "port": 993},
    "outlook": {"host": "outlook.office365.com", "port": 993},
    "yahoo": {"host": "imap.mail.yahoo.com", "port": 993},
    "custom": {"host": None, "port": 993},
}


@dataclass
class Config:
    email: str = ""
    password: str = ""
    provider: str = "gmail"
    imap_host: str = ""
    imap_port: int = 993
    spam_folder: str = '"[Gmail]/Spam"'
    interval_seconds: int = 3600
    dry_run: bool = False
    once: bool = False
    log_file: str = "spam_deleter.log"
    oauth2_enabled: bool = False
    oauth2_provider: str = ""
    oauth2_client_id: str = ""
    oauth2_client_secret: str = ""
    oauth2_refresh_token: str = ""


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        prog="spam_deleter",
        description="Elimina correos de la carpeta SPAM automáticamente.",
    )
    p.add_argument(
        "--interval",
        default=os.getenv("INTERVAL", "1h"),
        help="Intervalo entre limpiezas (ej: 30m, 2h, 1d). Default: 1h",
    )
    p.add_argument("--once", action="store_true", default=False, help="Ejecutar una sola vez y salir")
    p.add_argument("--dry-run", action="store_true", default=False, help="Solo listar correos sin borrar")
    p.add_argument("--provider", default=os.getenv("PROVIDER", ""), help="Proveedor (gmail, outlook, yahoo, custom)")
    p.add_argument("--log-file", default=os.getenv("LOG_FILE", "spam_deleter.log"), help="Ruta del archivo de log")
    return p.parse_args(argv)


def parse_interval(text: str) -> int:
    text = text.strip().lower()
    if text.endswith("s"):
        return int(text[:-1])
    if text.endswith("m"):
        return int(text[:-1]) * 60
    if text.endswith("h"):
        return int(text[:-1]) * 3600
    if text.endswith("d"):
        return int(text[:-1]) * 86400
    return int(text)


def build_config(argv: list[str] | None = None) -> Config:
    args = parse_args(argv)

    provider = (args.provider or os.getenv("PROVIDER") or "gmail").lower()
    prov = PROVIDERS.get(provider, PROVIDERS["custom"])

    cfg = Config(
        email=os.getenv("EMAIL", ""),
        password=os.getenv("PASSWORD", ""),
        provider=provider,
        imap_host=args.provider if provider == "custom" and args.provider else (os.getenv("IMAP_SERVER") or prov["host"] or ""),
        imap_port=int(os.getenv("IMAP_PORT") or prov["port"]),
        spam_folder=os.getenv("SPAM_FOLDER", _default_spam_folder(provider)),
        interval_seconds=parse_interval(args.interval),
        dry_run=args.dry_run,
        once=args.once,
        log_file=args.log_file,
        oauth2_enabled=os.getenv("OAUTH2_ENABLED", "").lower() in ("true", "1", "yes"),
        oauth2_provider=os.getenv("OAUTH2_PROVIDER", ""),
        oauth2_client_id=os.getenv("OAUTH2_CLIENT_ID", ""),
        oauth2_client_secret=os.getenv("OAUTH2_CLIENT_SECRET", ""),
        oauth2_refresh_token=os.getenv("OAUTH2_REFRESH_TOKEN", ""),
    )

    _validate(cfg)
    return cfg


def _default_spam_folder(provider: str) -> str:
    folders = {
        "gmail": '"[Gmail]/Spam"',
        "outlook": "Junk",
        "yahoo": "Bulk Mail",
    }
    return folders.get(provider, "SPAM")


def _validate(cfg: Config) -> None:
    missing = []
    if not cfg.email:
        missing.append("EMAIL")
    if not cfg.oauth2_enabled and not cfg.password:
        missing.append("PASSWORD")
    if not cfg.imap_host:
        missing.append("IMAP_SERVER")
    if missing:
        raise SystemExit(f"Faltan variables requeridas: {', '.join(missing)}. Revisa tu archivo .env")
