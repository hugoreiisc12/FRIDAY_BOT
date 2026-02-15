from typing import List, Dict
from core.models import Produto, PreferenciasUsuario

class ProcessadorProdutos:
    """Processa e filtra listas brutas de produtos para objetos Produto."""

    @staticmethod
    def processar(produtos_brutos: List[Dict], preferencias: PreferenciasUsuario, max_resultados: int = 10) -> List[Produto]:
        produtos = []
        for p in produtos_brutos[:max_resultados]:
            produto = Produto(
                nome=p.get("nome") or p.get("title"),
                loja=p.get("loja"),
                preco=p.get("preco"),
                frete=p.get("frete"),
                total=p.get("total") or p.get("preco"),
                url=p.get("url"),
                avaliacao=p.get("avaliacao"),
                num_avaliacoes=p.get("num_avaliacoes"),
                marca=p.get("marca")
            )
            produtos.append(produto)
        return produtos

    @staticmethod
    def filtrar_por_preco(produtos: List[Produto], orcamento_max: float) -> List[Produto]:
        return [p for p in produtos if p.preco is not None and p.preco <= orcamento_max]

    @staticmethod
    def filtrar_por_marca(produtos: List[Produto], marca: str) -> List[Produto]:
        return [p for p in produtos if p.marca and p.marca.lower() == marca.lower()]

    @staticmethod
    def ordenar_por_relevancia(produtos: List[Produto]) -> List[Produto]:
        # Placeholder: ordenar por preço ascendente
        return sorted(produtos, key=lambda p: (p.preco if p.preco is not None else float('inf')))

    @staticmethod
    def analise_precos(produtos: List[Produto]) -> Dict[str, float]:
        precos = [p.preco for p in produtos if p.preco is not None]
        if not precos:
            return {"min": 0.0, "max": 0.0, "avg": 0.0}
        return {"min": min(precos), "max": max(precos), "avg": sum(precos) / len(precos)}
