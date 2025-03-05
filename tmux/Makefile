include ../utils.mk

INSTALL_TARGETS += \
	install-configs \
	install-tpm \
	install-tpm-plugins

install: $(INSTALL_TARGETS)

### CONFIGS

TMUX_DIR = $(HOME)/.config/tmux

CONFIGS += \
	tmux.conf

install-config-%:
	@$(call copy-file, $*, $(TMUX_DIR)/$*, "[tmux/config]")

install-configs: $(addprefix install-config-, $(CONFIGS))

update-config-%:
	@$(call copy-file, $(TMUX_DIR)/$*, $*, "[tmux/config]", "true")

update-configs: $(addprefix update-config-, $(CONFIGS))

### TPM

TPM_DIR = $(HOME)/.tmux/plugins/tpm
TPM_INSTALL_PLUGINS = $(TPM_DIR)/bin/install_plugins

install-tpm:
	@if [ -d "$(TPM_DIR)" ]; then \
		echo "[tmux/tpm] $(TPM_DIR) already exists, not cloning"; \
	else \
		echo "[tmux/tpm] Cloning tpm to $(TPM_DIR)"; \
		git clone https://github.com/tmux-plugins/tpm "$(TPM_DIR)"; \
	fi

install-tpm-plugins:
	@echo "[tmux/tpm-plugins] Installing plugins"; \
		$(TPM_INSTALL_PLUGINS) all
