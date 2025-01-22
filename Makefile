VENV_DIR := .venv
INSTALLED_MARKER := .venv/.installed
APP_SCRIPT := src/main.py
MAKEFLAGS += -s

all: run

$(VENV_DIR):
	python3 -m venv $(VENV_DIR)

$(INSTALLED_MARKER): $(VENV_DIR) requirements.txt
	. $(VENV_DIR)/bin/activate && pip install -r requirements.txt
	@touch $(INSTALLED_MARKER)

run: $(INSTALLED_MARKER)
	-@. $(VENV_DIR)/bin/activate && python $(APP_SCRIPT) && deactivate

clean:
	rm -rf $(VENV_DIR)
	rm -f $(INSTALLED_MARKER)
