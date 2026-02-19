from connectors.mercado_livre import MercadoLivreConnector
from connectors.amazon import AmazonConnector
from services.normalization_service import normalize_products
from services.validation_service import validate_products
from ai.decision_engine import analyze_products


def get_products(query: str):
    """Orquestra múltiplos conectores, garante fallback e prepara dados para IA.

    Fluxo:
    - Validação simples da query (retorna vazio para queries curtas/vazias)
    - Tenta múltiplos conectores (MercadoLivre, Amazon...)
    - Em caso de erro em qualquer conector, registra e continua
    - Normaliza e valida resultados
    - Chama engine de decisão para análise/score

    Retorno:
        { "query": query, "results": validated_products, "decision": decision }
    """
    # Guard: query vazia ou muito curta => retorno vazio (consistente com product_service)
    if not query or len(query.strip()) < 2:
        return {"query": query, "results": [], "decision": analyze_products([])}

    connectors = [
        MercadoLivreConnector(),
        AmazonConnector(),
    ]

    raw_products = []

    for connector in connectors:
        try:
            raw_products.extend(connector.search(query))
        except Exception as e:
            # garantir resiliência: um conector com falha não derruba o orquestrador
            print(f"Erro no conector {connector.__class__.__name__}: {e}")

    normalized = normalize_products(raw_products)
    validated = validate_products(normalized)

    decision = analyze_products(validated)

    return {
        "query": query,
        "results": validated,
        "decision": decision,
    }
