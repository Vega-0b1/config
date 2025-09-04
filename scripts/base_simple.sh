#!/bin/bash
set -e
pacman -Sy --needed \
wezterm \
bash-language-server \
lua-language-server \
wl-clipboard \
btop \
neovim \
ttf-meslo-nerd \
poppler \
jq \
fd \
fzf \
zoxide \
imagemagick \
ttf-fira-code \
lazygit \
zsh \
zsh-syntax-highlighting \
zsh-autosuggestions \
starship \
yazi

chsh -s $(which zsh) jcvega



systemctl start bluetooth
systemctl enable bluetooth

export EDITOR=nvim
sudo cp /home/jcvega/.config/zsh/.zshrc /home/jcvega
sudo cp /home/jcvega/.config/scripts/kanata.service /etc/systemd/system
sudo systemctl daemon-reload

