#!/usr/bin/env python3
"""Interactive .env generator based on .env.example

Usage:
    python scripts/setup_env.py        # interactive prompts
    python scripts/setup_env.py --from-env  # create .env from current environment variables
    python scripts/setup_env.py --yes  # accept defaults

The script will write `.env` with file mode 600 (owner read/write) to avoid accidental commits.
"""

import os
import stat
import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / '.env.example'
OUT = ROOT / '.env'


def parse_example(path: Path):
    if not path.exists():
        return {}
    data = {}
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        if '=' not in line:
            continue
        key, _, val = line.partition('=')
        data[key.strip()] = val.strip()
    return data


def write_env(values: dict, dest: Path):
    lines = []
    for k, v in values.items():
        lines.append(f"{k}={v}")
    dest.write_text('\n'.join(lines) + '\n')
    # set secure permissions (rw-------)
    try:
        os.chmod(dest, stat.S_IRUSR | stat.S_IWUSR)
    except Exception:
        pass


def interactive_setup(defaults: dict, accept_defaults: bool = False):
    values = {}
    for k, default in defaults.items():
        env_val = os.getenv(k)
        shown_default = env_val or default or ''
        if accept_defaults:
            val = shown_default
        else:
            prompt = f"{k} [{shown_default}]: "
            try:
                val = input(prompt).strip()
            except KeyboardInterrupt:
                print('\nAborted by user')
                raise
            if val == '':
                val = shown_default
        values[k] = val
    return values


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--from-env', action='store_true', help='Create .env from existing environment variables')
    parser.add_argument('--yes', action='store_true', help='Accept defaults / env values without prompting')
    args = parser.parse_args()

    defaults = parse_example(EXAMPLE)
    if not defaults:
        print('Warning: .env.example not found or empty. You may still use --from-env to create .env from environment variables.')

    if args.from_env:
        values = {k: os.getenv(k, v) for k, v in defaults.items()}
    else:
        values = interactive_setup(defaults, accept_defaults=args.yes)

    # Confirm
    print('\nWriting .env with the following keys:')
    for k in values:
        print('-', k)

    write_env(values, OUT)
    print(f".env written to {OUT}")
    print("Permissions set to owner read/write (600) when possible.")
    print('\nNext steps:')
    print('- Export in your shell: export $(cat .env | xargs)')
    print('- Configure your secrets in your deployment environment (Heroku/GCP/GitHub Secrets)')


if __name__ == '__main__':
    main()
