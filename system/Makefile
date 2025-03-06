include ../utils.mk

INSTALL_TARGETS += \
	install-configs

UNAME_S := $(shell uname -s)

ifeq ($(UNAME_S),Linux)

	INSTALL_TARGETS += \
		install-apt-packages \
		install-python-packages

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

install: $(INSTALL_TARGETS)

### CONFIGS

install-config-%:
	@$(call copy-file, $*, $(HOME)/$*, "[system/config]", $(FORCE))

install-configs: $(addprefix install-config-, $(CONFIGS))

update-configs:

### APT

APT = /usr/bin/apt

install-apt-package-%:
	@$(APT) install $*

install-apt-packages: $(addprefix install-apt-package-, $(APT_PACKAGES))

### HOMEBREW

SH_C = sh -c
BREW = /opt/homebrew/bin/brew

install-homebrew:
	@$(SH_C) "$(curl -fsSL 'https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh')"

install-homebrew-package-%:
	@$(BREW) install $*

install-homebrew-packages: $(addprefix install-homebrew-package-, $(HOMEBREW_PACKAGES))

### PYTHON

PYTHON = /usr/bin/python3
PIP = $(PYTHON) -m pip

install-python-package-%:
	$(PIP) install $*

install-python-packages: $(addprefix install-python-package-, $(PYTHON_PACKAGES))
