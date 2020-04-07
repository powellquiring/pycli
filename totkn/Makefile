activate:
	@echo source venv/bin/activate

init: venv pipupgrade install

venv:
	python3 -m venv venv --prompt totkn

pipupgrade:
	pip install --upgrade pip

install:
	pip install requirements.txt

freeze:
	pip freeze > requirements.txt

editable:
	pip install -e .

mypy:
	mypy *.py test

tktn01:
	kubectl apply -f tktn01.yaml
	tkn pipeline start pipeline --showlog
