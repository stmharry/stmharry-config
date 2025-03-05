include ../utils.mk

INSTALL_TARGETS += \
	install-configs

install: install-configs

### CONFIGS

NVIM_DIR = $(HOME)/.config/nvim/

install-configs:
	@$(call copy-dir, nvim/, $(NVIM_DIR), "[nvim/config]")

update-configs:
	@$(call copy-dir, $(NVIM_DIR), nvim/, "[nvim/config]", "true")
