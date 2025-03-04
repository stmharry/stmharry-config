GMAILCTL_DIR = $(HOME)/.gmailctl
GMAILCTL_CONFIG_PATH = $(GMAILCTL_DIR)/config.jsonnet

install: install-gmailctl install-config

install-gmailctl:
	@echo "[gmailctl] Installing gmailctl"; \
		go install github.com/mbrt/gmailctl/cmd/gmailctl@latest; \
		gmailctl init

install-config:
	@if [ -f "$(GMAILCTL_CONFIG_PATH)" ]; then \
		echo "[gmailctl/config] $(GMAILCTL_CONFIG_PATH) already exists, not overwriting"; \
	else \
		echo "[gmailctl/config] Copying config.jsonnet to $(GMAILCTL_CONFIG_PATH)"; \
		mkdir -p "$(GMAILCTL_DIR)" && \
		cp config.jsonnet "$(GMAILCTL_CONFIG_PATH)"; \
	fi
