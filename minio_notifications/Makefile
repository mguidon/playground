.venv:
# target: .venv – Creates a python virtual environment with dev tools (pip, pylint, ...)
	python3 -m venv .venv
	.venv/bin/pip3 install --upgrade pip wheel setuptools
	.venv/bin/pip3 install pylint autopep8 virtualenv pip-tools
	@echo "To activate the venv, execute 'source .venv/bin/activate' or '.venv/Scripts/activate.bat' (WIN)"