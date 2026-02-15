# Boot Automático

Pequeno projeto para gravação de tela e automação com Selenium.

Estrutura principal:

- `gravacao_teste/` - implementação da gravação de tela (`Grav`).
- `Dependenciais/` - helpers relacionados a dependências (ex.: `WebDriverFactory`).
- `scripts/` - scripts de execução (ex.: `run_record.py`).
- `tests/` - testes com `pytest`.

Como usar (recomendado):

1. Criar e ativar um ambiente virtual:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

2. Instalar dependências:

   ```bash
   pip install -r requirements.txt
   ```

3. Executar exemplo de gravação:

   ```bash
   python scripts/run_record.py
   ```

Permissões (macOS): conceda permissão de `Gravação de Tela` ao Terminal/Python em Preferências do Sistema → Privacidade & Segurança.

---

## Nova arquitetura (scaffold)

Este workspace foi atualizado com um scaffold da arquitetura "Sexta Feira Bot" (core, ai, database, interfaces, payments, utils, scripts, tests, docs).
- Veja `docs/ARQUITETURA_COMPLETA.md` para o diagrama e instruções iniciais.
- **LangChain & RAG:** há um scaffold para RAG (`ai/rag.py`) e vector DB (`ai/vector_db.py`). Instale `requirements_langchain.txt` para ativar integrações reais.
- Execute `python scripts/run_tests.py` para rodar os testes iniciais (`pytest`).

Se preferir que eu reestruture mais arquivos ou implemente funcionalidades específicas, diga qual módulo devo priorizar.
