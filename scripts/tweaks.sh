#!/bin/bash

# Define the path to the loader configuration
LOADER_CONF="/efi/loader/loader.conf"

# Check if the file exists
if [ ! -f "$LOADER_CONF" ]; then
    echo "Creating $LOADER_CONF..."
    mkdir -p "$(dirname "$LOADER_CONF")"
    echo "timeout 1" > "$LOADER_CONF"
else
    # If the timeout line exists, replace it. Otherwise, append it.
    if grep -q '^timeout' "$LOADER_CONF"; then
        sed -i 's/^timeout.*/timeout 1/' "$LOADER_CONF"
    else
        echo "timeout 0.5" >> "$LOADER_CONF"
    fi
fi

echo "✅ systemd-boot timeout set to 1s in $LOADER_CONF"



echo "Updating /etc/systemd/logind.conf..."

# Replace or set HandleLidSwitch and HandleLidSwitchDocked
sudo sed -i \
    -e 's/^#\?HandleLidSwitch=.*/HandleLidSwitch=hibernate/' \
    -e 's/^#\?HandleLidSwitchDocked=.*/HandleLidSwitchDocked=ignore/' \
    /etc/systemd/logind.conf

# If those lines didn't exist, append them
grep -q '^HandleLidSwitch=' /etc/systemd/logind.conf || echo 'HandleLidSwitch=hibernate' | sudo tee -a /etc/systemd/logind.conf
grep -q '^HandleLidSwitchDocked=' /etc/systemd/logind.conf || echo 'HandleLidSwitchDocked=ignore' | sudo tee -a /etc/systemd/logind.conf

echo "Restarting systemd-logind..."
sudo systemctl restart systemd-logind

echo "Done. You can now test hibernation with: sudo systemctl hibernate"

