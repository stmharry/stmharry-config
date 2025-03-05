include ../utils.mk

INSTALL_TARGETS += \
	install-configs \
	install-gmailctl

install: $(INSTALL_TARGETS)

### CONFIGS

GMAILCTL_DIR = $(HOME)/.gmailctl

CONFIGS += \
	config.jsonnet

install-config-%:
	@$(call copy-file, $*, $(GMAILCTL_DIR)/$*, "[gmailctl/config]")

install-configs: $(addprefix install-config-, $(CONFIGS))

update-config-%:
	@$(call copy-file, $(GMAILCTL_DIR)/$*, $*, "[gmailctl/config]", "true")

update-configs: $(addprefix update-config-, $(CONFIGS))

### GMAILCTL

install-gmailctl:
	@echo "[gmailctl] Installing gmailctl"; \
		go install github.com/mbrt/gmailctl/cmd/gmailctl@latest; \
		gmailctl init
