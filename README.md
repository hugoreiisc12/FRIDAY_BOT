# Boot Automático

Sexta Feira Bot — assistente de compras conversacional (backend Python) focado em busca, comparação, negociação e checkout via conectores e LLMs.

Estrutura principal:

- `ai/` — ConversationManager, RAG, vector DB e providers (`ai/providers/`).
- `services/` — conectores de API (ex.: `product_service.py`).
- `interfaces/` — FastAPI e Telegram (ex.: `interfaces/api.py`, `interfaces/run_telegram.py`).
- `database/` — stores (ex.: `database/supabase_store.py`).
- `tests/` — suíte de testes (pytest).

Rápido: executar localmente

1. Criar e ativar venv:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   # (opcional) para RAG/langchain: pip install -r requirements_langchain.txt
   ```

2. Configurar variáveis de ambiente (ex.: `.env`):

   - `TELEGRAM_BOT_TOKEN` — token do bot Telegram (opcional)
   - `LLM_PROVIDER` — `hf-router` | `hf` | `openai` | `mock`
   - `HF_API_TOKEN` / `HF_TOKEN` — Hugging Face
   - `SUPABASE_URL` / `SUPABASE_KEY` — para persistência (opcional)

3. Executar API (FastAPI):

   ```bash
   python scripts/run_api.py
   # depois: http://localhost:8000/docs
   ```

4. Rodar Telegram (polling):

   ```bash
   source .env && python interfaces/run_telegram.py
   ```

---

## Nova arquitetura (scaffold)

Este workspace foi atualizado com um scaffold da arquitetura "Sexta Feira Bot" (core, ai, database, interfaces, payments, utils, scripts, tests, docs).
- Veja `docs/ARQUITETURA_COMPLETA.md` para o diagrama e instruções iniciais.
- **LangChain & RAG:** há um scaffold para RAG (`ai/rag.py`) e vector DB (`ai/vector_db.py`). Instale `requirements_langchain.txt` para ativar integrações reais.
- Execute `python scripts/run_tests.py` para rodar os testes iniciais (`pytest`).

Se preferir que eu reestruture mais arquivos ou implemente funcionalidades específicas, diga qual módulo devo priorizar.
