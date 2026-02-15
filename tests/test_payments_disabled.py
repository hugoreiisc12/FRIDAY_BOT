from payments.payments import PaymentManager


def test_payment_manager_manual():
    pm = PaymentManager()
    pm.enabled = False
    res = pm.criar_checkout_carrinho("user1", [{"nome": "X", "preco": 100}], email_cliente=None)
    assert res.get("manual") is True
    assert "manual" in res and "mensagem" in res
