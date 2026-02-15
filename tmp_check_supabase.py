from interfaces import api as api_module
from core.supabase_store import SupabaseConversationStore
import os, time

CM = api_module.CM
print('CM.store initially:', bool(getattr(CM, 'store', None)))
if not getattr(CM, 'store', None):
    CM.store = SupabaseConversationStore(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'))
    print('Attached SupabaseConversationStore')

uid = 'persistence_test_user'
print('Starting conversation for', uid)
resp = CM.iniciar_conversa(uid, 'Tester')
print('Intro length:', len(resp))
CM.processar_mensagem(uid, '1')
CM.processar_mensagem(uid, 'Quero um notebook Dell 8GB')

ctx = CM.obter_contexto(uid)
print('session_id on ctx:', getattr(ctx, 'session_id', None))
msgs = CM.store.get_messages(ctx.session_id)
print('Stored messages count:', len(msgs))
for m in msgs[-6:]:
    print(m['role'], m['content'][:120])
