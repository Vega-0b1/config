#!/usr/bin/env bash
# Bluetooth connection monitor - shows notifications on connect/disconnect

get_device_name() {
    bluetoothctl info "$1" 2>/dev/null | grep -oP 'Name: \K.*' || echo "Unknown Device"
}

notify() {
    local action="$1"
    local device="$2"
    local icon

    if [[ "$action" == "connected" ]]; then
        icon="bluetooth-active-symbolic"
        notify-send -a "bluetooth" -r 9992 -t 3000 \
            -h "string:x-canonical-private-synchronous:bluetooth" \
            "Bluetooth Connected" "$device" \
            -i "$icon"
    else
        icon="bluetooth-disabled-symbolic"
        notify-send -a "bluetooth" -r 9992 -t 3000 \
            -h "string:x-canonical-private-synchronous:bluetooth" \
            "Bluetooth Disconnected" "$device" \
            -i "$icon"
    fi
}

# Monitor bluetoothctl for connection events
bluetoothctl | while read -r line; do
    if [[ "$line" == *"Device"*"Connected: yes"* ]]; then
        mac=$(echo "$line" | grep -oP 'Device \K[A-F0-9:]+')
        name=$(get_device_name "$mac")
        notify "connected" "$name"
    elif [[ "$line" == *"Device"*"Connected: no"* ]]; then
        mac=$(echo "$line" | grep -oP 'Device \K[A-F0-9:]+')
        name=$(get_device_name "$mac")
        notify "disconnected" "$name"
    fi
done
