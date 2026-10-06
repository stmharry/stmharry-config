# Keep user-installed CLIs visible to noninteractive SSH shells too.
# No commands, plugin loading, or output in this file.
typeset -U path
path=("$HOME/.local/bin" "$HOME/bin" "$HOME/.bun/bin" "$HOME/go/bin" /usr/local/go/bin /usr/local/bin $path)
export PATH
