NVIM_DIR = $(HOME)/.config/nvim

install: install-config

install-config:
	@if [ -d "$(NVIM_DIR)" ]; then \
		echo "[nvim/config] $(NVIM_DIR) already exists, not overwriting"; \
	else \
		echo "[nvim/config] Copying nvim to $(NVIM_DIR)"; \
		cp -r . "$(NVIM_DIR)"; \
	fi
