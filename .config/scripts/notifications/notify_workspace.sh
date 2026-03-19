#!/usr/bin/env bash
# Workspace OSD — call with workspace number as argument

declare -A NAMES=(
    [1]="Algorithms"
    [2]="Paradigms"
    [3]="Web Dev"
    [4]="Diversity"
    [5]="3D Printing"
    [10]="Scratch"
)

N="${1:-}"
NAME="${NAMES[$N]:-Workspace $N}"

notify-send -a "workspace" -r 9992 -t 2000 \
    -h "string:x-canonical-private-synchronous:workspace" \
    "Workspace $N" "$NAME"
