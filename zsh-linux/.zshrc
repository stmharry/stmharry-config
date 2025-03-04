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

# thefuck

eval "$(thefuck --alias --enable-experimental-instant-mode)"

# aliases

alias l="ls"
alias ll="ls -alh"
alias du="du -h"
alias vim="nvim"
