# Gravação de Tela (grav.py)

Instruções rápidas para configurar o ambiente e executar:

1. Criar e ativar ambiente virtual (recomendado):

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

2. Instalar dependências:

   ```bash
   pip install -r requirements.txt
   ```

3. Permissões no macOS:

   - Vá em Preferências do Sistema → Privacidade & Segurança → Gravação de Tela e ative o Terminal/Python para permitir captura de tela.

4. Exemplo mínimo de uso:

   ```python
   import time
   from grav import Grav

   g = Grav()
   nome = g.iniciar_gravacao("teste")
   time.sleep(5)  # grava por 5 segundos
   g.parar_gravacao()
   print(f"Arquivo salvo: {nome}")
   ```

Se tiver problemas com a captura de tela no macOS, verifique as permissões e instale `pyobjc-framework-Quartz` (já listado em `requirements.txt`).
