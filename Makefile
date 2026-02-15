install:
	python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt

test:
	pytest -q

run-example:
	python scripts/run_record.py
