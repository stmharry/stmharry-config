include ../utils.mk

INSTALL_TARGETS += \
	install-configs

install: install-configs

### CONFIGS

FORCE ?= false
NVIM_DIR = $(HOME)/.config/nvim/

install-configs:
	@$(call copy-dir, nvim/, $(NVIM_DIR), "[nvim/config]", $(FORCE))

update-configs:
	@$(call copy-dir, $(NVIM_DIR), nvim/, "[nvim/config]", "true")
