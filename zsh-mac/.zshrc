### ZSH

export ZSH="${HOME}/.oh-my-zsh"

ZSH_THEME="robbyrussell"
ENABLE_CORRECTION="true"
plugins=(git)

source "${ZSH}/oh-my-zsh.sh"

### USER

# environment

export PATH="${HOME}/bin:${HOME}/.local/bin:/usr/local/bin:${PATH}"

export LANG=en_US.UTF-8
export LC_ALL=en_US.UTF-8
export EDITOR="nvim"
export GPG_TTY=${TTY}

# iterm2

test -e "${HOME}/.iterm2_shell_integration.zsh" && source "${HOME}/.iterm2_shell_integration.zsh" || true

# homebrew

export PATH="/opt/homebrew/bin:${PATH}"
eval "$(brew shellenv)"

# thefuck

eval "$(thefuck --alias --enable-experimental-instant-mode)"

# aliases

alias l="ls"
alias ll="ls -alh"
alias du="du -h"
alias vim="nvim"

alias ssh-tw-ws="ssh -p 6999 chia@ap-gateway.stmharry.io"
