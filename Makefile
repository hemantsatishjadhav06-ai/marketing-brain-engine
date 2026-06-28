.PHONY: install smoke test discover create publish engage analyze setup lint
install:; pip install -r requirements.txt
smoke:; DRY_RUN=true python -m scripts.run_stage all
test:; python -m pytest -q
discover:; python -m scripts.run_stage discover
create:; python -m scripts.run_stage create
publish:; python -m scripts.run_stage publish
engage:; python -m scripts.run_stage engage
analyze:; python -m scripts.run_stage analyze
setup:; python -m scripts.setup_airtable
lint:; python -m compileall marketing_brain scripts
