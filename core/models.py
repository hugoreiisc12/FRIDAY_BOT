from dataclasses import dataclass, field
from typing import List, Dict, Optional

@dataclass
class Produto:
    nome: str
    loja: Optional[str] = None
    preco: Optional[float] = None
    frete: Optional[float] = None
    total: Optional[float] = None
    url: Optional[str] = None
    avaliacao: Optional[float] = None
    num_avaliacoes: Optional[int] = None
    marca: Optional[str] = None
    meta: Dict = field(default_factory=dict)

@dataclass
class PreferenciasUsuario:
    produto: Optional[str] = None
    marca: Optional[str] = None
    cor: Optional[str] = None
    tamanho: Optional[str] = None
    orcamento_max: Optional[float] = None
    loja: Optional[str] = None

@dataclass
class IntencaoUsuario:
    tipo: Optional[str] = None  # buscar, refinar, selecionar, etc
    confianca: Optional[float] = None
    produto: Optional[str] = None
    numero_produto: Optional[int] = None
    extras: Dict = field(default_factory=dict)

@dataclass
class EstadoConversa:
    user_id: str
    etapa_atual: str = "INICIAL"
    preferencias: PreferenciasUsuario = field(default_factory=PreferenciasUsuario)
    produtos_encontrados: List[Produto] = field(default_factory=list)
    produto_selecionado: Optional[Produto] = None
    historico_mensagens: List[Dict] = field(default_factory=list)
