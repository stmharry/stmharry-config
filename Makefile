include utils.mk

TARGETS += \
	system \
	zsh \
	tmux \
	git \
	astronvim

default: install

install-%:
	@make -C $* install

install: $(addprefix install-, $(TARGETS))
