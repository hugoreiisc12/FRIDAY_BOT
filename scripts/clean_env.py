"""Script para limpar valores sensíveis do arquivo .env local.

- Faz backup em `.env.bak`
- Remove/limpa valores das chaves sensíveis listadas
- NÃO comita alterações automaticamente
"""
import shutil
from pathlib import Path

ENV_PATH = Path('.env')
BACKUP_PATH = Path('.env.bak')
SENSITIVE_KEYS = [
     'HF_TOKEN', 'HF_API_TOKEN', 'GEMINI_API_KEY',
    'PINECONE_API_KEY', 'SUPABASE_KEY', 'TELEGRAM_BOT_TOKEN',
    'MP_ACCESS_TOKEN', 'MP_ACCESS_TOKEN_SANDBOX'
]

if not ENV_PATH.exists():
    print('.env not found; nothing to do')
    raise SystemExit(0)

shutil.copy2(ENV_PATH, BACKUP_PATH)
print(f'Backup criado: {BACKUP_PATH}')

lines = ENV_PATH.read_text().splitlines()
new_lines = []
for ln in lines:
    stripped = ln.strip()
    if not stripped or stripped.startswith('#'):
        new_lines.append(ln)
        continue
    key = ln.split('=', 1)[0].strip()
    if key in SENSITIVE_KEYS:
        new_lines.append(f'{key}=')
        print(f'Limpei {key}')
    else:
        new_lines.append(ln)

ENV_PATH.write_text('\n'.join(new_lines) + '\n')
print('Limpeza concluída. Verifique .env.bak para backup.')
