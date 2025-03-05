TARGETS += \
	system \
	zsh \
	tmux \
	astronvim

install-%:
	@make -C $* install

install: $(addprefix install-, $(TARGETS))

update-configs-%:
	@make -C $* update-configs

update-configs: $(addprefix update-configs-, $(TARGETS))
