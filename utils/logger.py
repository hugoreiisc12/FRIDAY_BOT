import logging

class BotLogger:
    def __init__(self, name: str = "sexta-feira-bot"):
        self.logger = logging.getLogger(name)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

    def user(self, mensagem: str):
        self.logger.info(f"[USER] {mensagem}")

    def bot(self, mensagem: str):
        self.logger.info(f"[BOT] {mensagem}")

    def system(self, mensagem: str):
        self.logger.info(f"[SYSTEM] {mensagem}")

    def error(self, mensagem: str, exception: Exception = None):
        self.logger.error(f"[ERROR] {mensagem} - {exception}")


class LoggerManager:
    def __init__(self):
        self.loggers = {}

    def obter(self, nome: str = "default") -> BotLogger:
        if nome not in self.loggers:
            self.loggers[nome] = BotLogger(nome)
        return self.loggers[nome]
