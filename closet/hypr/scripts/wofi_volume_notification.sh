#!/bin/bash

# Get the current volume and mute state
VOLUME=$(wpctl get-volume @DEFAULT_AUDIO_SINK@ | awk '{print int($2 * 100)}')
MUTED=$(wpctl get-mute @DEFAULT_AUDIO_SINK@)

if [ "$MUTED" == "true" ]; then
    MESSAGE="🔇 Muted"
else
    MESSAGE="      Volume: $VOLUME"

fi

# Use the notification-specific Wofi config and style
echo "$MESSAGE" | wofi --conf ~/.config/wofi/notifications/config --dmenu --height 8% --width 10%  --style ~/.config/wofi/notifications/volume.css &
WOFI_PID=$!

# Close Wofi after 2 seconds
sleep 1
kill "$WOFI_PID" 2>/dev/null
