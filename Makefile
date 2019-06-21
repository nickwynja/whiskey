# http://blog.bottlepy.org/2012/07/16/virtualenv-and-makefiles.html
VENV_PATH = .venv

venv: $(VENV_PATH)/bin/activate

.venv/bin/activate: requirements.txt
	test -d $(VENV_PATH) || virtualenv $(VENV_PATH)
	$(shell which pip3) install --src $(VENV_PATH)/src -r requirements.txt
	touch $(VENV_PATH)/bin/activate

lint:
	flake8 whiskey
