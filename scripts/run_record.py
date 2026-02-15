#!/usr/bin/env python3
"""Script de exemplo: grava 3 segundos da tela."""
import time
from gravacao_teste.grav import Grav


def main():
    g = Grav()
    nome = g.iniciar_gravacao("exemplo")
    print(f"Gravando por 3s: {nome}")
    time.sleep(3)
    g.parar_gravacao()
    print(f"Arquivo salvo: {nome}")


if __name__ == '__main__':
    main()
