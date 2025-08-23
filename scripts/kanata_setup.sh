#!/bin/bash
yay -Syu kanata-bin \
wezterm-git \
grimblast \
hyprland-git \
zen-browser-bin \
ags-hyprpanel-git \
--noconfirm
# Define user (adjust if running this for another user)
#KANATA_USER="${KANATA_USER:-$USER}"
#KANATA_GROUP="kanata"

# 1. Create kanata group (if it doesn't exist)
#sudo groupadd -f "$KANATA_GROUP"

# 2. Add user to kanata group
#sudo usermod -aG "$KANATA_GROUP" "$KANATA_USER"

# 3. Create udev rule for uinput
#sudo tee /etc/udev/rules.d/99-kanata-uinput.rules > /dev/null <<EOF
#KERNEL=="uinput", GROUP="$KANATA_GROUP", MODE="660", OPTIONS+="static_node=uinput"
#EOF

# 4. Reload udev rules
#sudo udevadm control --reload-rules
#sudo udevadm trigger

#cp /home/jcvega/.config/scripts/kanata.service /etc/systemd/system
# 8. Reload systemd user daemon
#systemctl --user daemon-reexec
#systemctl --user daemon-reload

# 9. Enable and start Kanata user service
systemctl enable --now kanata.service


