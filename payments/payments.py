import os

class MercadoPagoService:
    def __init__(self, access_token: str = None, sandbox: bool = True):
        self.access_token = access_token
        self.sandbox = sandbox

    def criar_link_pagamento(self, titulo, descricao, valor, email_cliente=None, external_reference=None):
        if not self.access_token:
            raise RuntimeError("Mercado Pago não configurado")
        return {"init_point": "https://pagamento.exemplo", "preference_id": "pref_123"}

    def consultar_pagamento(self, payment_id: str):
        if not self.access_token:
            raise RuntimeError("Mercado Pago não configurado")
        return {"status": "pending", "id": payment_id}

    def processar_webhook(self, dados: dict):
        # process webhook payload
        return {"ok": True}


class PaymentManager:
    """High-level manager. By default payments are disabled and manual checkout is expected."""

    def __init__(self):
        self.enabled = os.getenv("PAYMENTS_ENABLED", "false").lower() == "true"
        token = os.getenv("MP_ACCESS_TOKEN") or os.getenv("MP_ACCESS_TOKEN_SANDBOX")
        if self.enabled and not token:
            raise RuntimeError("PAYMENTS_ENABLED is true but MP_ACCESS_TOKEN is missing")
        self.service = MercadoPagoService(access_token=token) if self.enabled else None

    def criar_checkout_carrinho(self, telegram_id, carrinho, email_cliente=None):
        if not self.enabled:
            # Return manual instruction to user
            return {"manual": True, "mensagem": "Para finalizar a compra, por favor acesse o site do vendedor e conclua o checkout manualmente. Posso gerar um resumo da compra para você encaminhar."}
        # Implement real checkout flow when enabled
        return self.service.criar_link_pagamento(titulo="Compra", descricao="Carrinho", valor=sum(p.get('preco', 0) for p in carrinho), email_cliente=email_cliente)
