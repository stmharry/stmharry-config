### ZSH

export ZSH="${HOME}/.oh-my-zsh"

ZSH_THEME="stmharry"
ENABLE_CORRECTION="true"
plugins=(virtualenv git)

source "${ZSH}/oh-my-zsh.sh"

### USER

# environment

export PATH="${HOME}/bin:${HOME}/.local/bin:/usr/local/bin:${PATH}"

export LANG=en_US.UTF-8
export LC_ALL=en_US.UTF-8
export EDITOR="nvim"
export GPG_TTY=${TTY}

# iterm2

if [ -f "${HOME}/.iterm2_shell_integration.zsh" ]; then
  source "${HOME}/.iterm2_shell_integration.zsh"
fi

# homebrew

if [ -d "/opt/homebrew" ]; then
  export PATH="/opt/homebrew/bin:${PATH}"
  eval "$(brew shellenv)"
fi

# thefuck

eval "$(thefuck --alias --enable-experimental-instant-mode)"

# aliases

alias l="ls"
alias ll="ls -alh"
alias du="du -h"
alias vim="nvim"

alias ssh-tw-ws="ssh -p 6999 chia@ap-gateway.stmharry.io"
