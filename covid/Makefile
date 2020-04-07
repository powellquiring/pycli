activate:
	@echo source venv/bin/activate

init: venv pipupgrade install

venv:
	python3 -m venv venv --prompt covid

pipupgrade:
	pip install --upgrade pip

install:
	pip install requirements.txt

freeze:
	pip freeze > requirements.txt

installme:
	pip install -e .

