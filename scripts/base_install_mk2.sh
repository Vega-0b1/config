#!/bin/bash
set -e
pacman -Syu \
neovim \
kitty \
freecad \
ttf-meslo-nerd \
cliphist \
poppler \
jq \
fd \
fzf \
zoxide \
imagemagick \
wl-clipboard \
ttf-fira-code \
lazygit \
zsh \
zsh-syntax-highlighting \
zsh-autosuggestions \
starship \

hyprland \
hypridle \
hyprpaper \
waybar \
grim \
slurp \
dunst \
wofi \
wl-clipboard \

--noconfirm
chsh -s $(which zsh)

git config --global user.name "jcvega"
git config --global user.email "jcvega0b1@gmail.com"
git config --global credential.helper store

systemctl start bluetooth
systemctl enable bluetooth
