#!/usr/bin/env bash
# Volume OSD for PipeWire/wpctl + mako

set -euo pipefail

ACTION="${1:-}"
STEP="${2:-5}"
SINK="${SINK:-@DEFAULT_AUDIO_SINK@}"

[[ "$ACTION" =~ ^(up|down|mute)$ ]] || { echo "Usage: $0 {up|down|mute} [step]" >&2; exit 1; }

# Apply change
case "$ACTION" in
    up)   wpctl set-mute "$SINK" 0; wpctl set-volume "$SINK" "${STEP}%+" --limit 1.0 ;;
    down) wpctl set-mute "$SINK" 0; wpctl set-volume "$SINK" "${STEP}%-" ;;
    mute) wpctl set-mute "$SINK" toggle ;;
esac

# Read state
out="$(wpctl get-volume "$SINK" 2>/dev/null || echo "Volume: 0")"
volf="$(awk '{print $2}' <<< "$out")"
pct="$(awk -v v="${volf:-0}" 'BEGIN{printf("%.0f", v*100)}')"
muted=$([[ "$out" == *"[MUTED]"* ]] && echo 1 || echo 0)

# Select icon
if (( muted || pct == 0 )); then
    icon="audio-volume-muted-symbolic"
elif (( pct < 34 )); then
    icon="audio-volume-low-symbolic"
elif (( pct < 67 )); then
    icon="audio-volume-medium-symbolic"
else
    icon="audio-volume-high-symbolic"
fi

# Build progress bar
filled=$(( pct / 10 ))
empty=$(( 10 - filled ))
bar="$(printf '█%.0s' $(seq 1 $filled 2>/dev/null) || true)$(printf '░%.0s' $(seq 1 $empty 2>/dev/null) || true)"

# Notification
if (( muted )); then
    notify-send -a "volume" -r 9990 -t 1500 \
        -h "string:x-canonical-private-synchronous:volume" \
        -h "int:value:0" \
        "Volume Muted" "░░░░░░░░░░" \
        -i "$icon"
else
    notify-send -a "volume" -r 9990 -t 1200 \
        -h "string:x-canonical-private-synchronous:volume" \
        -h "int:value:${pct}" \
        "Volume ${pct}%" "$bar" \
        -i "$icon"
fi
