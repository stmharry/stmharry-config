TARGETS += \
	zsh \
	tmux \
	astronvim \
	gmailctl

install-%:
	@make -C $* install

install: $(addprefix install-, $(TARGETS))

update-configs-%:
	@make -C $* update-configs

update-configs: $(addprefix update-configs-, $(TARGETS))
