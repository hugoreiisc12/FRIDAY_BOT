import os
from typing import Optional, Dict, Any, List

try:
    from supabase import create_client
except Exception as e:
    create_client = None


class SupabaseConversationStore:
    """Simple Supabase-backed conversation store.

    Usage:
      store = SupabaseConversationStore(url, key)
      store.create_session(ctx)  # creates session and sets ctx.session_id
      store.save_message(ctx, role, content)
      store.get_messages(session_id)

    Requires SUPABASE_URL and SUPABASE_KEY in env (or passed in constructor).
    """

    def __init__(self, url: Optional[str] = None, key: Optional[str] = None):
        self.url = url or os.getenv("SUPABASE_URL")
        self.key = key or os.getenv("SUPABASE_KEY")
        if not self.url or not self.key:
            raise RuntimeError("SUPABASE_URL and SUPABASE_KEY must be provided")
        if create_client is None:
            raise RuntimeError("supabase package not available")
        self.client = create_client(self.url, self.key)

    def create_session(self, ctx) -> Dict[str, Any]:
        payload = {
            "user_id": ctx.user_id,
            "estado": ctx.estado.value if ctx.estado else None,
            "modo": ctx.modo_acao.value if ctx.modo_acao else None,
            "metadata": {"nome_usuario": ctx.nome_usuario},
        }
        res = self.client.table("sessions").insert(payload).execute()
        # supabase returns data in res.data
        data = getattr(res, "data", None)
        if not data:
            raise RuntimeError(f"Failed to create session: {getattr(res, 'error', res)}")
        row = data[0] if isinstance(data, list) else data
        ctx.session_id = row.get("id")
        return row

    def save_message(self, ctx, role: str, content: str, metadata: Optional[Dict] = None) -> Dict[str, Any]:
        # ensure session
        session_id = getattr(ctx, "session_id", None)
        if not session_id:
            sess = self.create_session(ctx)
            session_id = sess.get("id")
        payload = {
            "session_id": session_id,
            "user_id": ctx.user_id,
            "role": role,
            "content": content,
            "metadata": metadata or {},
        }
        res = self.client.table("messages").insert(payload).execute()
        data = getattr(res, "data", None)
        if not data:
            raise RuntimeError(f"Failed to save message: {getattr(res, 'error', res)}")
        return data[0] if isinstance(data, list) else data

    def get_messages(self, session_id: str) -> List[Dict[str, Any]]:
        res = self.client.table("messages").select("*").eq("session_id", session_id).order("created_at", desc=False).execute()
        return getattr(res, "data", [])

