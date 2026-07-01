from __future__ import annotations

import time
from email import message_from_bytes
from typing import TYPE_CHECKING

from .connector import connect
from .logger import SpamLogger

if TYPE_CHECKING:
    from .config import Config


def clean_spam(config: "Config", log: SpamLogger) -> None:
    log.info("Conectando a %s como %s ...", config.provider, config.email)
    try:
        mail = connect(config)
    except Exception as e:
        log.error(f"Error de conexion: {e}")
        return

    try:
        status, _ = mail.select(config.spam_folder)
        if status != "OK":
            log.error(f"No se pudo abrir la carpeta {config.spam_folder}")
            return

        status, data = mail.search(None, "ALL")
        if status != "OK" or not data[0]:
            log.info("No hay correos en SPAM.")
            return

        ids = data[0].split()
        log.info(f"Encontrados {len(ids)} correos en SPAM.")

        start = time.perf_counter()
        deleted = 0

        for mid in ids:
            status, msg_data = mail.fetch(mid, "(BODY.PEEK[HEADER.FIELDS (FROM SUBJECT)])")
            if status != "OK":
                continue

            sender, subject = _parse_envelope(msg_data)

            if config.dry_run:
                log.dry_run(config.provider, sender, subject)
            else:
                mail.store(mid, "+FLAGS", "\\Deleted")
                log.delete(config.provider, sender, subject)
                deleted += 1

        if not config.dry_run and deleted > 0:
            mail.expunge()

        elapsed = time.perf_counter() - start
        final_count = deleted if not config.dry_run else len(ids)
        log.summary(config.provider, final_count, elapsed)

    finally:
        try:
            mail.close()
            mail.logout()
        except Exception:
            pass


def _parse_envelope(msg_data: list[bytes]) -> tuple[str, str]:
    sender = "(desconocido)"
    subject = "(sin asunto)"
    try:
        for part in msg_data:
            if isinstance(part, bytes):
                msg = message_from_bytes(part)
                sender = str(msg.get("From", sender))
                subject = str(msg.get("Subject", subject))
    except Exception:
        pass
    return sender, subject
