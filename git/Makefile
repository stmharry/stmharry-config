include ../utils.mk

INSTALL_TARGETS += \
	install-configs

install: $(INSTALL_TARGETS)

### CONFIGS

CONFIGS += \
	.gitconfig \
	.gitmessage.txt

install-config-%:
	@$(call copy-file, $*, $(HOME)/$*, "[git/config]")

install-configs: $(addprefix install-config-, $(CONFIGS))

update-config-%:
	@$(call copy-file, $(HOME)/$*, $*, "[git/config]", "true")

update-configs: $(addprefix update-config-, $(CONFIGS))
