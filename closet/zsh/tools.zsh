## FZF keybindings (Ctrl+R, Ctrl+T, etc.)
[ -f ~/.fzf.zsh ] && source ~/.fzf.zsh Zoxide: smart directory jumping
eval "$(zoxide init zsh)"
eval "$(starship init zsh)"

function y() {
	local tmp="$(mktemp -t "yazi-cwd.XXXXXX")" cwd
	yazi "$@" --cwd-file="$tmp"
	IFS= read -r -d '' cwd < "$tmp"
	[ -n "$cwd" ] && [ "$cwd" != "$PWD" ] && builtin cd -- "$cwd"
	rm -f -- "$tmp"
}



