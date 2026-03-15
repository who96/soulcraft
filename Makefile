.PHONY: test compile lint clean

test:
	pytest tests/ -v

compile:
	python -m compiler.compile --all

compile-one:
	python -m compiler.compile souls/$(SOUL)/soul.yaml

lint:
	python -m py_compile compiler/compile.py
	python -m py_compile l0_adapter/cli.py

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -name '*.pyc' -delete
