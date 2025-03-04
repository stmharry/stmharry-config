install: install-configs install-homebrew-packages install-oh-my-zsh

# configs

CONFIG_TARGETS = \
	install-config-.zshrc \
	install-config-Harry.json

install-config-%:
	@if [ -f "$(HOME)/$*" ]; then \
		echo "[shell/config] $(HOME)/$* already exists, not overwriting"; \
	else \
		echo "[shell/config] Copying $* to $(HOME)/$*"; \
		cp $* "$(HOME)/$*"; \
	fi

install-configs: $(CONFIG_TARGETS)

# homebrew

install-homebrew:
	sh -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

HOMEBREW_TARGETS = \
	install-homebrew-package-zsh \
	install-homebrew-package-neovim

install-homebrew-package-%:
	brew install $*

install-homebrew-packages: $(HOMEBREW_TARGETS)

# zsh

install-oh-my-zsh:
	sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"
