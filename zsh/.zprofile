# Homebrew environment for login shells (Apple Silicon, Intel, or Linux).
for brew_bin in /opt/homebrew/bin/brew /usr/local/bin/brew /home/linuxbrew/.linuxbrew/bin/brew; do
  if [[ -x "$brew_bin" ]]; then
    eval "$("$brew_bin" shellenv)"
    break
  fi
done
unset brew_bin

# nvm selects its default Node for noninteractive login shells as well.
export NVM_DIR="$HOME/.nvm"
if [[ -s "$NVM_DIR/nvm.sh" ]] && (( ! $+functions[nvm] )); then
  source "$NVM_DIR/nvm.sh"
fi
