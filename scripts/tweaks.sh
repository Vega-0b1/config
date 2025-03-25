#!/bin/bash
#run as root
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
        echo "timeout 1" >> "$LOADER_CONF"
    fi
fi

echo "✅ systemd-boot timeout set to 1s in $LOADER_CONF"
