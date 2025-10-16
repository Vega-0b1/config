# Safer file operations
alias rm='rm -i'
alias cp='cp -i'
alias mv='mv -i'

# Navigation
alias ..='cd ..'
alias ...='cd ../..'
alias c='clear'
alias l='ls -lah --color=auto'
alias la='ls -A'
alias ll='ls -l'

# Git shortcuts
alias gs='git status'
alias ga='git add'
alias gc='git commit'
alias gp='git push'
alias gl='git log --oneline --graph --decorate'

# System stuff
alias pacs='sudo pacman -S'
alias pacr='sudo pacman -R'
alias update='sudo pacman -Syu'

# Neovim
alias v='nvim'
alias vz='nvim ~/.zshrc'
alias vc='nvim ~/.config/zsh'

# Dotfiles
alias dots='cd ~/.config && nvim'

