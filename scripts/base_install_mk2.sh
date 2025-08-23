#!/bin/bash
#chsh -s $(which zsh) $USER
set -e
pacman -Syu \
sddm \
hyprland \
thunar \
thunar-archive-plugin \
thunar-volman \
bash-language-server \
brightnessctl \
hyprpicker \
btop \
neovim \
ttf-meslo-nerd \
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
hypridle \
wofi \
wl-clipboard \
libgtop \
dart-sass \
gvfs \
gtksourceview3 \
libsoup3 \
yazi  \
--noconfirm

echo "setting up git defaults"
git config --global user.name "jcvega"
git config --global user.email "jcvega0b1@gmail.com"
git config --global credential.helper store

systemctl start bluetooth
systemctl enable bluetooth

export EDITOR=nvim
sudo cp /home/jcvega/.config/zsh/.zshrc /home/jcvega
sudo cp /home/jcvega/.config/scripts/kanata.service /etc/systemd/system
systemctl enable sddm
systemctl start sddm
