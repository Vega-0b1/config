#!/usr/bin/env bash
# Brightness OSD for brightnessctl + mako

set -euo pipefail

ACTION="${1:-}"
STEP="${2:-5}"

[[ "$ACTION" =~ ^(up|down)$ ]] || { echo "Usage: $0 {up|down} [step]" >&2; exit 1; }

# Prefer backlight device if available
DEVICE_OPT=""
brightnessctl -l 2>/dev/null | grep -q '\bbacklight\b' && DEVICE_OPT="-c backlight"

get_pct() {
    local cur max
    cur="$(brightnessctl $DEVICE_OPT get)"
    max="$(brightnessctl $DEVICE_OPT max)"
    (( max == 0 )) && echo 0 || echo $(( cur * 100 / max ))
}

pct_before="$(get_pct)"

# Smart stepping: 1% under 5%, configurable step above
if [[ "$ACTION" == "down" ]]; then
    if (( pct_before <= 5 )); then
        target=$(( pct_before - 1 ))
        (( target < 1 )) && target=1
    elif (( pct_before % STEP == 0 )); then
        target=$(( pct_before - STEP ))
    else
        target=$(( (pct_before / STEP) * STEP ))
    fi
else
    if (( pct_before < 5 )); then
        target=$(( pct_before + 1 ))
    elif (( pct_before < STEP )); then
        target=$STEP
    elif (( pct_before % STEP == 0 )); then
        target=$(( pct_before + STEP ))
    else
        target=$(( ((pct_before + STEP - 1) / STEP) * STEP ))
    fi
    (( target > 100 )) && target=100
fi

brightnessctl $DEVICE_OPT -q set "${target}%"
pct_after="$(get_pct)"

# Select icon based on brightness level
if (( pct_after <= 33 )); then
    icon="display-brightness-low-symbolic"
elif (( pct_after <= 66 )); then
    icon="display-brightness-medium-symbolic"
else
    icon="display-brightness-high-symbolic"
fi

# Build progress bar
filled=$(( pct_after / 10 ))
empty=$(( 10 - filled ))
bar="$(printf '█%.0s' $(seq 1 $filled 2>/dev/null) || true)$(printf '░%.0s' $(seq 1 $empty 2>/dev/null) || true)"

notify-send -a "brightness" -r 9991 -t 1200 \
    -h "string:x-canonical-private-synchronous:brightness" \
    -h "int:value:${pct_after}" \
    "Brightness ${pct_after}%" "$bar" \
    -i "$icon"
