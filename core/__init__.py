# core domain package (models + processors)
from .models import Produto, PreferenciasUsuario
from .processors import ProcessadorProdutos

# NOTE: provider and store implementations were moved to `ai.providers` and `database`.
# The old `core.services_*` modules now provide deprecated shims that re-export the new
# implementations to maintain backward compatibility.

__all__ = ["Produto", "PreferenciasUsuario", "ProcessadorProdutos"]
