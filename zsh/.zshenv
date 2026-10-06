# Keep user-installed CLIs visible to noninteractive SSH shells too.
# No plugin loading or output in this file.
typeset -U path
path=("$HOME/.local/bin" "$HOME/bin" "$HOME/.bun/bin" "$HOME/go/bin" /usr/local/go/bin /usr/local/bin $path)
export PATH

# Preserve host-local environment settings for noninteractive sessions too.
[[ -f "$HOME/.zshenv.local" ]] && source "$HOME/.zshenv.local"
true
