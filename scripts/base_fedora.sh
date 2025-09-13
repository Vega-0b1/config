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
  clang-tools-extra \
  black \
  rust \
  cargo \
  zsh \
  zsh-autosuggestions \
  zsh-syntax-highlighting \
  hyprland \
  fira-code-fonts \
  thunar \
  thunar-archive-plugin \
  thunar-volman \
  btop \
  blueman \
  network-manager-applet \

 chsh -s $(which zsh) jcvega
 curl -sS https://starship.rs/install.sh | sh
 
cargo install stylua
cargo install kanata
export PATH="$HOME/.cargo/bin:$PATH"

