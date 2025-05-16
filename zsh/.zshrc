### ZSH

export ZSH="${HOME}/.oh-my-zsh"

ZSH_THEME="stmharry"

# tmux

ZSH_TMUX_AUTONAME_SESSION=true

plugins=(
  tmux
  virtualenv
)

source "${ZSH}/oh-my-zsh.sh"

### USER

# environment

export PATH="${HOME}/bin:${HOME}/.local/bin:/usr/local/bin:${PATH}"

export LANG=en_US.UTF-8
export LC_ALL=en_US.UTF-8
export EDITOR="nvim"
export GPG_TTY=${TTY}

# aliases

alias l="ls"
alias ll="ls -alh"
alias du="du -h"
alias vim="nvim"
alias ssh-tw-ws="ssh -p 6999 chia@ap-gateway.stmharry.io"

# secrets

[ -f "$HOME/.zsh_secrets" ] && . "$HOME/.zsh_secrets"

# iterm2

[ -f "${HOME}/.iterm2_shell_integration.zsh" ] && . "${HOME}/.iterm2_shell_integration.zsh"

# homebrew

[ -f "/home/linuxbrew/.linuxbrew/bin/brew" ] && eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)"

# nvm

export NVM_DIR="$HOME/.nvm"
[ -f "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh"
[ -f "$NVM_DIR/bash_completion" ] && . "$NVM_DIR/bash_completion"

# bun

export PATH="${HOME}/.bun/bin:$PATH"

# go

export GOPATH="${HOME}/go"
[ -d "${GOPATH}" ] && export PATH="${GOPATH}/bin:${PATH}"

# thefuck

eval "$(thefuck --alias --enable-experimental-instant-mode)"

alias f="fuck"
alias ff="fuck --yeah"
