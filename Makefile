.PHONY: install test quick all clean

install:
	python -m pip install -e .

test:
	python -m pytest -q

quick:
	python scripts/04_vqe_exact_fci.py --molecule h2 --mapper parity --maxiter 200

all:
	python scripts/run_all.py

clean:
	rm -f results/data/*.json results/data/*.csv results/figures/*.png
