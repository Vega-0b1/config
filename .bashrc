# Source system bashrc if it exists
[[ -f /etc/bashrc ]] && . /etc/bashrc
[[ -f /etc/bash.bashrc ]] && . /etc/bash.bashrc

# PATH
export PATH="$HOME/.cargo/bin:$HOME/.local/bin:$PATH"

# Aliases
alias home='cd "$HOME"'
alias dl='cd "$HOME/Downloads"'
alias doc='cd "$HOME/Documents"'
alias config='cd "$HOME/.config"'
alias archconfig='cd "$HOME/config"'
alias edu='cd "$HOME/edu"'
alias doodle='cd "$HOME/edu/doodle"'
