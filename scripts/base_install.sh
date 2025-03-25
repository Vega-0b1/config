#!/bin/bash
set -e
pacman -Syu \
sddm \
hyprland \
hyprlock \
neovim \
kitty \
wofi \
ttf-meslo-nerd \
waybar \
hyprpaper \
cliphist \
dunst \
hypridle \
blueman \
network-manager-applet \
ffmpeg \
7zip \
poppler \
jq \
fd \
fzf \
zoxide \
imagemagick \
wl-clipboard \
ttf-fira-code \
grim \
slurp \
lazygit \
eos-sddm-theme \
--noconfirm


# Get current user (non-root) for messages, but no autologin used
USER_NAME="${SUDO_USER:-$(whoami)}"

# Ensure we're root
if [ "$EUID" -ne 0 ]; then
  echo "❌ Please run as root (e.g., sudo $0)"
  exit 1
fi

echo "🚀 Enabling SDDM service..."
systemctl enable sddm

# Ensure Hyprland session file exists
SESSION_FILE="/usr/share/wayland-sessions/Hyprland.desktop"
if [ ! -f "$SESSION_FILE" ]; then
  echo "⚠️ Hyprland session file not found. Creating it..."

  cat > "$SESSION_FILE" <<EOF
[Desktop Entry]
Name=Hyprland
Comment=An intelligent dynamic tiling Wayland compositor
Exec=Hyprland
Type=Application
DesktopNames=Hyprland
EOF

  echo "✅ Created $SESSION_FILE"
else
  echo "✅ Hyprland session file already exists."
fi

systemctl start bluetooth
systemctl enable bluetooth 

git config --global user.name "jcvega"
git config --global user.email "jcvega0b1@gmail.com"
