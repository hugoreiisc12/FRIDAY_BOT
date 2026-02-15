from core.processors import ProcessadorProdutos
from core.models import PreferenciasUsuario


def test_processar_e_filtrar():
    produtos_brutos = [
        {"nome": "A", "preco": 100.0, "marca": "X"},
        {"nome": "B", "preco": 200.0, "marca": "Y"},
        {"nome": "C", "preco": 50.0, "marca": "X"},
    ]
    prefs = PreferenciasUsuario()
    produtos = ProcessadorProdutos.processar(produtos_brutos, prefs, max_resultados=10)
    assert len(produtos) == 3
    filtrados = ProcessadorProdutos.filtrar_por_marca(produtos, "X")
    assert len(filtrados) == 2
    filtrados_preco = ProcessadorProdutos.filtrar_por_preco(produtos, 100.0)
    assert all(p.preco <= 100.0 for p in filtrados_preco)
