include ../utils.mk

### INSTALL

INSTALL_TARGETS += \
	install-configs \
	install-oh-my-zsh \
	install-oh-my-zsh-themes

install: $(INSTALL_TARGETS)

### CONFIGS

FORCE ?= false
CONFIGS += \
	.zshrc

install-config-%:
	@$(call copy-file, $*, $(HOME)/$*, "[zsh/config]", $(FORCE))

install-configs: $(addprefix install-config-, $(CONFIGS))

update-config-%:
	@$(call copy-file, $(HOME)/$*, $*, "[zsh/config]", "true")

update-configs: $(addprefix update-config-, $(CONFIGS))

### OH_MY_ZSH

SH_C = sh -c

OH_MY_ZSH_DIR = $(HOME)/.oh-my-zsh
OH_MY_ZSH_THEME_DIR = $(OH_MY_ZSH_DIR)/custom/themes

OH_MY_ZSH_THEMES += \
	stmharry.zsh-theme

install-oh-my-zsh:
	@$(SH_C) "$(curl -fsSL 'https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh')"

install-oh-my-zsh-theme-%:
	@$(call copy-file, $*, $(OH_MY_ZSH_THEME_DIR)/$*, "[zsh/oh-my-zsh-theme]", $(FORCE))

install-oh-my-zsh-themes: $(addprefix install-oh-my-zsh-theme-, $(OH_MY_ZSH_THEMES))

update-oh-my-zsh-theme-%:
	@$(call copy-file, $(OH_MY_ZSH_THEME_DIR)/$*, $*, "[zsh/oh-my-zsh-theme]", "true")

update-oh-my-zsh-themes: $(addprefix update-oh-my-zsh-theme-, $(OH_MY_ZSH_THEMES))
