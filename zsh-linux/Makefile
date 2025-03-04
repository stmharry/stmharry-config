PYTHON = /usr/bin/python3

install: install-configs install-oh-my-zsh

# configs

CONFIG_TARGETS = \
	install-config-.zshrc

install-config-%:
	@if [ -f "$(HOME)/$*" ]; then \
		echo "[shell/config] $(HOME)/$* already exists, not overwriting"; \
	else \
		echo "[shell/config] Copying $* to $(HOME)/$*"; \
		cp $* "$(HOME)/$*"; \
	fi

install-configs: $(CONFIG_TARGETS)

# python

PYTHON_TARGETS = \
	install-python-package-thefuck

install-python-package-%:
	$(PYTHON) -m pip install $*

install-python-packages: $(PYTHON_TARGETS)

# zsh

install-oh-my-zsh:
	sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"
