# Enable completions
autoload -Uz compinit
compinit

# History settings
HISTFILE=~/.zsh_history
HISTSIZE=10000
SAVEHIST=10000
setopt inc_append_history
setopt share_history

# Keybindings
bindkey '^R' fzf-history-widget

