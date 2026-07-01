import logging


class SpamLogger:
    def __init__(self, filepath: str) -> None:
        self.logger = logging.getLogger("spam_deleter")
        self.logger.setLevel(logging.INFO)
        self.logger.handlers.clear()

        fmt = logging.Formatter("%(asctime)s | %(message)s", datefmt="%Y-%m-%d %H:%M:%S")

        fh = logging.FileHandler(filepath, encoding="utf-8")
        fh.setFormatter(fmt)
        self.logger.addHandler(fh)

        ch = logging.StreamHandler()
        ch.setFormatter(fmt)
        self.logger.addHandler(ch)

    def delete(self, provider: str, sender: str, subject: str) -> None:
        subject_clean = subject.replace("|", "/").strip()[:80] or "(sin asunto)"
        sender_clean = sender.replace("|", "/").strip()[:80] or "(desconocido)"
        self.logger.info("DELETE  | %s | %s | %s", provider, sender_clean, subject_clean)

    def dry_run(self, provider: str, sender: str, subject: str) -> None:
        subject_clean = subject.replace("|", "/").strip()[:80] or "(sin asunto)"
        sender_clean = sender.replace("|", "/").strip()[:80] or "(desconocido)"
        self.logger.info("DRY-RUN | %s | %s | %s", provider, sender_clean, subject_clean)

    def summary(self, provider: str, count: int, elapsed: float) -> None:
        self.logger.info("SUMMARY | %s | Eliminados: %d correos en %.2fs", provider, count, elapsed)

    def error(self, msg: str) -> None:
        self.logger.error("ERROR   | %s", msg)

    def info(self, msg: str, *args: object) -> None:
        self.logger.info("INFO    | " + msg, *args)
