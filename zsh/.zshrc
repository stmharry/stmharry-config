### Shell and prompt
export ZSH="$HOME/.oh-my-zsh"
ZSH_THEME="stmharry"
ZSH_TMUX_AUTONAME_SESSION=true
plugins=(git tmux virtualenv)
# Startup must remain usable while an agent installs prerequisites.
[[ -f "$ZSH/oh-my-zsh.sh" ]] && source "$ZSH/oh-my-zsh.sh"

export EDITOR="nvim"
export VISUAL="nvim"
[[ -n "$TTY" ]] && export GPG_TTY="$TTY"

alias l="ls"
alias ll="ls -alh"
alias du="du -h"
alias vim="nvim"
if ! command -v fd >/dev/null 2>&1 && command -v fdfind >/dev/null 2>&1; then
  alias fd="fdfind"
fi

### Optional integrations
[[ -f "$HOME/.zsh_secrets" ]] && source "$HOME/.zsh_secrets"
[[ -f "$HOME/.iterm2_shell_integration.zsh" ]] && source "$HOME/.iterm2_shell_integration.zsh"
[[ -d /usr/local/cuda/bin ]] && path=(/usr/local/cuda/bin $path)
export NVM_DIR="$HOME/.nvm"
if [[ -s "$NVM_DIR/nvm.sh" ]] && (( ! $+functions[nvm] )); then
  source "$NVM_DIR/nvm.sh"
fi
export GOPATH="${GOPATH:-$HOME/go}"
[[ -d "$GOPATH/bin" ]] && path=("$GOPATH/bin" $path)
if command -v thefuck >/dev/null 2>&1; then
  eval "$(thefuck --alias --enable-experimental-instant-mode)"
  alias f="fuck"
  alias ff="fuck --yeah"
fi
command -v direnv >/dev/null 2>&1 && eval "$(direnv hook zsh)"

# Host/project environment hooks and personal overrides stay outside Git.
[[ -f "$HOME/.zshrc.local" ]] && source "$HOME/.zshrc.local"
true
