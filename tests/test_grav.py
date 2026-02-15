import pytest
from gravacao_teste.grav import Grav


def test_grav_init():
    g = Grav()
    assert g.get_nome_arquivo() == ""
    assert hasattr(g, 'iniciar_gravacao')
    assert hasattr(g, 'parar_gravacao')
