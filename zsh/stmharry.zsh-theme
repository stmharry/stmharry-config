PROMPT=""

PROMPT+=$'\n'
PROMPT+="%{$fg_bold[cyan]%}%~%{$reset_color%}"
PROMPT+='$(git_prompt_info)'
PROMPT+='$(virtualenv_prompt_info)'
PROMPT+=" …"
PROMPT+=$'\n'
PROMPT+="%(?:%{$fg_bold[green]%}%1{➜%} :%{$fg_bold[red]%}%1{➜%} )%{$reset_color%}"

ZSH_THEME_GIT_PROMPT_PREFIX=" on %{$fg_bold[red]%} "
ZSH_THEME_GIT_PROMPT_DIRTY="%{$fg[blue]%}%{$fg[yellow]%}%1{ ✗%}"
ZSH_THEME_GIT_PROMPT_CLEAN="%{$fg[blue]%}"
ZSH_THEME_GIT_PROMPT_SUFFIX="%{$reset_color%}"

ZSH_THEME_VIRTUALENV_PREFIX=" via %{$fg_bold[blue]%}"
ZSH_THEME_VIRTUALENV_SUFFIX="%{$reset_color%}"
