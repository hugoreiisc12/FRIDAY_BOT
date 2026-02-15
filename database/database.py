# Minimal DatabaseManager stub
from typing import Dict, Any, List

class DatabaseManager:
    def __init__(self, dsn: str = None):
        self.dsn = dsn

    def criar_usuario(self, telegram_id: str, nome: str) -> int:
        # Placeholder: return fake id
        return 1

    def salvar_sessao(self, telegram_id: str, preferencias: Dict[str, Any], etapa: str):
        pass

    def carregar_sessao(self, telegram_id: str) -> Dict[str, Any]:
        return {}

    # ... outros métodos a implementar
