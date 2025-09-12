#!/bin/bash
dnf copr enable -y wezfurlong/wezterm-nightly
dnf copr enable -y lihaohong/yazi 
dnf copr enable -y agriffis/neovim-nightly
dnf copr enable -y solopasha/hyprland
dnf install -y \
  git \
  yazi \
  alacritty \
  neovim \
  python3-neovim \
  clang \
  cmake \
  hyprland-scanner-devel \
  clang-tools-extra \
  black \
  rust \
  cargo \
  zsh \
  zsh-autosuggestions \
  zsh-syntax-highlighting \
  hyprland \
  hypridle \
  hyprlock \
  hyprpaper \
  waybar \
  fira-code-fonts \
  thunar \
  thunar-archive-plugin \
  thunar-volman \
  btop \
  wofi \
  pavucontrol \
  blueman \
  network-manager-applet \
  hyprpaper \
  hypridle \
  hyprlock \
  hyprpolkitagent \
  waypaper


wget https://github.com/ryanoasis/nerd-fonts/releases/download/v2.1.0/Meslo.zip
unzip Meslo.zip -d ~/MesloNerdFont
mkdir -p ~/.local/share/fonts
cp ~/MesloNerdFont/*.ttf ~/.local/share/fonts/
fc-cache -fv

 chsh -s $(which zsh) jcvega
 curl -sS https://starship.rs/install.sh | sh

 
cargo install stylua
cargo install kanata
export PATH="$HOME/.cargo/bin:$PATH"

