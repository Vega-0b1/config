#!/bin/bash
echo "installing main packages"
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
waybar \
grim \
slurp \
dunst \
wofi \
wl-clipboard \
blueman \
network-manager-applet \
yazi  \
--noconfirm
echo "done"

echo "setting up git defaults"
git config --global user.name "jcvega"
git config --global user.email "jcvega0b1@gmail.com"
git config --global credential.helper store
echo "done"

echo "enabling bluetooth"
systemctl start bluetooth
systemctl enable bluetooth
echo "done"

export EDITOR=nvim

echo "running yay install"
./kanata_setup.sh
echo "yay is done
