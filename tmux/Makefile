TMUX_DIR = $(HOME)/.config/tmux
TMUX_CONFIG_PATH = $(TMUX_DIR)/tmux.conf
TPM_DIR = $(HOME)/.tmux/plugins/tpm

install: install-config install-tpm install-tpm-plugins

install-config:
	@if [ -f "$(TMUX_DIR)/tmux.conf" ]; then \
		echo "[tmux/config] $(TMUX_CONFIG_PATH) already exists, not overwriting"; \
	else \
		echo "[tmux/config] Copying tmux.conf to $(TMUX_CONFIG_PATH)"; \
		mkdir -p "$(TMUX_DIR)" && \
		cp tmux.conf "$(TMUX_CONFIG_PATH)"; \
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
