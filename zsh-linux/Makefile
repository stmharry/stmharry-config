PYTHON = /usr/bin/python3
OH_MY_ZSH_DIR = $(HOME)/.oh-my-zsh

install: install-configs install-oh-my-zsh install-oh-my-zsh-themes

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
	@sh -c "$(curl -fsSL 'https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh')"

install-oh-my-zsh-theme-%:
	@if [ -f "$(OH_MY_ZSH_DIR)/custom/themes/$*" ]; then \
		echo "[shell/oh-my-zsh] $(OH_MY_ZSH_DIR)/custom/themes/$* already exists, not overwriting"; \
	else \
		echo "[shell/oh-my-zsh] Copying $* to $(OH_MY_ZSH_DIR)/custom/themes/$*"; \
		cp $* "$(OH_MY_ZSH_DIR)/custom/themes/$*"; \
	fi

OH_MY_ZSH_THEME_TARGETS = \
	install-oh-my-zsh-theme-stmharry.zsh-theme

install-oh-my-zsh-themes: $(OH_MY_ZSH_THEME_TARGETS)
