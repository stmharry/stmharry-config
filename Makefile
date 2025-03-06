TARGETS += \
	system \
	zsh \
	tmux \
	git \
	astronvim

install-%:
	@make -C $* install

install: $(addprefix install-, $(TARGETS))

install-configs-%:
	@make -C $* install-configs

install-configs: $(addprefix install-configs-, $(TARGETS))

update-configs-%:
	@make -C $* update-configs

update-configs: $(addprefix update-configs-, $(TARGETS))
