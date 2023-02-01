VENV 			:=  test -d venv || python3.10 -m venv venv
INSTALL  		:= . venv/bin/activate && pip install --upgrade pip && pip install -r requirements.txt

install:venv
	@echo "Installing..."
	@$(INSTALL)
	@echo "Done."

venv:
	@echo "Creating venv..."
	@$(VENV)
	@echo "Done."

.PHONY: install venv