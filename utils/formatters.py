def formatar_produto_simples(produto: dict) -> str:
    nome = produto.get('nome', 'Produto')
    preco = produto.get('preco', 'n/a')
    loja = produto.get('loja', '-')
    url = produto.get('url', '')
    return f"{nome} — R$ {preco} — {loja}\n{url}"


def formatar_lista_produtos(produtos: list) -> str:
    linhas = []
    for i, p in enumerate(produtos, start=1):
        linhas.append(f"{i}) {p.get('nome','Produto')} — R$ {p.get('preco','n/a')}")
    return "\n".join(linhas)
