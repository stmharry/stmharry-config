include ../utils.mk

UNAME_S := $(shell uname -s)

ifeq ($(UNAME_S),Linux)

	INSTALL_TARGETS += \
		install-apt-packages

	APT_PACKAGES += \
		golang-go \
		git \
		git-delta \
		neovim

	PYTHON_PACKAGES += \
		thefuck

else ifeq ($(UNAME_S),Darwin)  # macOS

	CONFIGS += \
		Harry.json

	INSTALL_TARGETS += \
		install-homebrew \
		install-homebrew-packages

	HOMEBREW_PACKAGES += \
		go \
		git \
		git-delta \
		neovim \
		thefuck

endif

### UTILS

SH_C = sh -c

### INSTALL

INSTALL_TARGETS += \
	install-configs \
	install-oh-my-zsh \
	install-oh-my-zsh-themes \
	install-python-packages

install: $(INSTALL_TARGETS)

### CONFIGS

CONFIGS += \
	.zshrc

install-config-%:
	@$(call copy-file, $*, $(HOME)/$*, "[shell/config]")

install-configs: $(addprefix install-config-, $(CONFIGS))

update-config-%:
	@$(call copy-file, $(HOME)/$*, $*, "[shell/config]", "true")

update-configs: $(addprefix update-config-, $(CONFIGS))

### APT

APT = /usr/bin/apt

install-apt-package-%:
	@$(APT) install $*

install-apt-packages: $(addprefix install-apt-package-, $(APT_PACKAGES))

### OH_MY_ZSH

OH_MY_ZSH_DIR = $(HOME)/.oh-my-zsh
OH_MY_ZSH_THEME_DIR = $(OH_MY_ZSH_DIR)/custom/themes

OH_MY_ZSH_THEMES += \
	stmharry.zsh-theme

install-oh-my-zsh:
	@$(SH_C) "$(curl -fsSL 'https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh')"

install-oh-my-zsh-theme-%:
	@$(call copy-file, $*, $(OH_MY_ZSH_THEME_DIR)/$*, "[shell/oh-my-zsh-theme]")

install-oh-my-zsh-themes: $(addprefix install-oh-my-zsh-theme-, $(OH_MY_ZSH_THEMES))

### PYTHON

PYTHON = /usr/bin/python3
PIP = $(PYTHON) -m pip

install-python-package-%:
	$(PIP) install $*

install-python-packages: $(addprefix install-python-package-, $(PYTHON_PACKAGES))

### HOMEBREW

BREW = /opt/homebrew/bin/brew

install-homebrew:
	@$(SH_C) "$(curl -fsSL 'https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh')"

install-homebrew-package-%:
	@$(BREW) install $*

install-homebrew-packages: $(addprefix install-homebrew-package-, $(HOMEBREW_PACKAGES))
