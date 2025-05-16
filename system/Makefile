include ../utils.mk

INSTALL_TARGETS += \
	install-configs

UNAME_S := $(shell uname -s)

ifeq ($(UNAME_S),Linux)

	INSTALL_TARGETS += \
		install-apt-packages \
		install-homebrew \
		install-homebrew-packages \
		install-nvm

	APT_PACKAGES += \
		golang-go \
		git \
		git-delta \
		neovim

	HOMEBREW_PACKAGES += \
		oven-sh/bun/bun \
		thefuck \
		uv

else ifeq ($(UNAME_S),Darwin)  # macOS

	CONFIGS += \
		Harry.json

	INSTALL_TARGETS += \
		install-homebrew \
		install-homebrew-packages \
		install-nvm

	HOMEBREW_PACKAGES += \
		go \
		git \
		git-delta \
		neovim \
		oven-sh/bun/bun \
		thefuck \
		uv

endif

install: $(INSTALL_TARGETS)

### CONFIGS

install-config-%:
	@$(call copy-file, $*, $(HOME)/$*, "[system/config]", $(FORCE))

install-configs: $(addprefix install-config-, $(CONFIGS))

update-configs:

### APT

define install-apt-package
	$(eval $@_PACKAGE := $(1))
	@$(APT) install -y $($@_PACKAGE)
endef

install-apt-packages:
	@$(foreach package, $(APT_PACKAGES), $(call install-apt-package, "$(package)"))

### SHELL

define install-shell-package
	$(eval $@_URL := $(1))
	curl -fsSL $($@_URL) | bash
endef

### HOMEBREW

BREW = brew
HOMEBREW_SH_URL = https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh

define install-homebrew-package
	$(eval $@_PACKAGE := $(1))
	brew install $($@_PACKAGE)
endef

install-homebrew:
	@$(call install-shell-package, $(HOMEBREW_SH_URL))

install-homebrew-packages:
	@$(foreach package, $(HOMEBREW_PACKAGES), $(call install-homebrew-package, "$(package)"))

### NVM

NVM_SH_URL = https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.3/install.sh

install-nvm:
	@$(call install-shell-package, $(NVM_SH_URL))
