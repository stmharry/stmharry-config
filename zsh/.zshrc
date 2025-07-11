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
alias mosh-tw-ws="mosh chia@tw-ws.stmharry.io"

ssh-connect() {
  local user="chia" host="$1" opts=("${@:2}")

  echo "Trying: ssh ${opts[*]} ${user}@${host} ..."
  if ssh -o BatchMode=yes -o ConnectTimeout=5 "${opts[@]}" "${user}@${host}" exit &>/dev/null; then
    echo "✔ Connected to ${host}"
    exec ssh "${opts[@]}" "${user}@${host}"
  else
    return 1
  fi
}

ssh-tw-ws() {
  ssh-connect 192.168.0.41 || ssh-connect tw-ws.stmharry.io || ssh-connect ap-gateway.stmharry.io -p 6999
}

# secrets

[ -f "$HOME/.zsh_secrets" ] && . "$HOME/.zsh_secrets"

# iterm2

[ -f "${HOME}/.iterm2_shell_integration.zsh" ] && . "${HOME}/.iterm2_shell_integration.zsh"

# homebrew

[ -f "/home/linuxbrew/.linuxbrew/bin/brew" ] && eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)"

# cuda

export PATH="/usr/local/cuda/bin:${PATH}"

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
