import sys
import os
from typing import Optional

# ensure project root is on path
PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

from config.config import ConversationManager

app = FastAPI(title="Sexta Feira Bot API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Single manager instance
CM = ConversationManager()


class StartRequest(BaseModel):
    user_id: str
    name: Optional[str] = None


class MessageRequest(BaseModel):
    user_id: str
    message: str


@app.post("/start")
def start(req: StartRequest):
    resp = CM.iniciar_conversa(req.user_id, req.name or "Cliente")
    return {"resposta": resp}


@app.post("/message")
def message(req: MessageRequest):
    ctx = CM.obter_contexto(req.user_id)
    if not ctx:
        CM.iniciar_conversa(req.user_id)
    res = CM.processar_mensagem(req.user_id, req.message)
    return res


@app.get("/context/{user_id}")
def get_context(user_id: str):
    ctx = CM.obter_contexto(user_id)
    if not ctx:
        raise HTTPException(status_code=404, detail="context not found")
    # Return safe context
    return {
        "user_id": ctx.user_id,
        "estado": ctx.estado.value,
        "modo_acao": ctx.modo_acao.value if ctx.modo_acao else None,
        "carrinho": ctx.carrinho,
        "produtos": ctx.produtos[:10],
        "mensagens": ctx.mensagens[-20:],
    }


@app.get("/cart/{user_id}")
def get_cart(user_id: str):
    ctx = CM.obter_contexto(user_id)
    if not ctx:
        raise HTTPException(status_code=404, detail="context not found")
    return {"carrinho": ctx.carrinho, "total": sum([p.get("preco", 0) for p in ctx.carrinho])}


@app.post("/checkout/{user_id}")
def checkout(user_id: str):
    ctx = CM.obter_contexto(user_id)
    if not ctx:
        raise HTTPException(status_code=404, detail="context not found")
    # Trigger finalize flow
    CM.processar_mensagem(user_id, "4")
    res = CM.processar_mensagem(user_id, "Quero finalizar a compra")
    return res


@app.get('/history')
def get_history(user_id: str):
    """Return persisted conversation history for a given user_id (Supabase-backed).

    Priority:
      1) if ConversationManager has an in-memory context with session_id -> use it
      2) otherwise query Supabase sessions table for the latest session and return messages
    """
    # prefer in-memory context
    ctx = CM.obter_contexto(user_id)
    if ctx and getattr(ctx, 'session_id', None) and CM.store:
        try:
            msgs = CM.store.get_messages(ctx.session_id)
            return {"session_id": ctx.session_id, "messages": msgs}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"failed to read messages: {e}")

    # fallback to store lookup by user_id
    if CM.store:
        try:
            res = CM.store.client.table('sessions').select('*').eq('user_id', user_id).order('created_at', desc=True).limit(1).execute()
            data = getattr(res, 'data', []) or []
            if not data:
                raise HTTPException(status_code=404, detail='no session found for user')
            session_id = data[0].get('id')
            msgs = CM.store.get_messages(session_id)
            return {"session_id": session_id, "messages": msgs}
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    raise HTTPException(status_code=404, detail='no stored history available')


# Products router (connectors layer)
try:
    from interfaces.products import router as products_router
    app.include_router(products_router)
except Exception as e:
    print(f"⚠️ Não foi possível incluir router de produtos: {e}")
