import schedule
import time
from .config import Config
from .cleaner import clean_spam
from .logger import SpamLogger


def run(config: Config) -> None:
    log = SpamLogger(config.log_file)
    log.info("=" * 60)
    log.info(f"Iniciando SpamDeleter | Proveedor: {config.provider} | Email: {config.email}")
    if config.dry_run:
        log.info("Modo DRY-RUN: No se borrara ningun correo")
    log.info(f"Intervalo: cada {config.interval_seconds}s")
    log.info("=" * 60)

    if config.once:
        clean_spam(config, log)
        return

    clean_spam(config, log)
    schedule.every(config.interval_seconds).seconds.do(clean_spam, config, log)

    log.info(f"Esperando {config.interval_seconds}s hasta la proxima ejecucion...")

    while True:
        schedule.run_pending()
        time.sleep(1)
