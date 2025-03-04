TMUX_CONF_DIR = $(HOME)/.config/tmux
TPM_DIR = $(HOME)/.tmux/plugins/tpm

install: install-config install-tpm install-tpm-plugins

install-config:
	@if [ -f "$(TMUX_CONF_DIR)/tmux.conf" ]; then \
		echo "[tmux/config] $(TMUX_CONF_DIR)/tmux.conf already exists, not overwriting"; \
	else \
		echo "[tmux/config] Copying tmux.conf to $(TMUX_CONF_DIR)/tmux.conf"; \
		mkdir -p "$(TMUX_CONF_DIR)" && \
		cp tmux.conf "$(TMUX_CONF_DIR)/tmux.conf"; \
	fi

install-tpm:
	@if [ -d "$(TPM_DIR)" ]; then \
		echo "[tmux/tpm] $(TPM_DIR) already exists, not cloning"; \
	else \
		echo "[tmux/tpm] Cloning tpm to $(TPM_DIR)"; \
		git clone https://github.com/tmux-plugins/tpm "$(TPM_DIR)"; \
	fi

install-tpm-plugins:
	@echo "[tmux/tpm-plugins] Installing plugins"; \
		"$(TPM_DIR)/bin/install_plugins" all
