install: install-tmux install-gmailctl

install-%:
	@make -C $*
