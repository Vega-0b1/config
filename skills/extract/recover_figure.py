#!/usr/bin/env python3
"""Recover EPUB figures whose transparent background was flattened to black (diagrams.md D32a).

The flattened areas are pure black; ink drawn on them survives as very dark gray. Inside
each dark zone (large near-black areas plus the dark pixels connected to them), brightness
LOW..HIGH is inverted to white..black. Saturated colours, bright pixels, and everything
outside the dark zones are left untouched.

Usage:
    recover_figure.py <out_dir> [--compare <compare_dir>] <image> [<image> ...]

For each image, writes <out_dir>/<stem>.png when its dark zone covers at least MIN_SHARE of
the image (D32f); with --compare, also writes <compare_dir>/<stem>.png showing the original
and the recovered copy side by side for the D32c visual check.
"""

from collections import deque
from collections.abc import Sequence
import sys
from pathlib import Path

from PIL import Image

ZONE = 70        # brightness at or below which a pixel can belong to a dark zone
LOW = 10         # at or below: flattened background, becomes white
HIGH = 45        # at or above (up to ZONE): ink, becomes black
SEED_AREA = 30   # pure-black areas at least this large start a dark zone
GROW = 2         # dilation so anti-aliased ink edges join the zone
CHROMA = 40      # channel spread above which a pixel is a saturated colour, kept as drawn
TINT = 12        # blue minus red at or above which a dark pixel is the edge of blue ink
SATURATION = 0.6  # blue-minus-red share of blue that marks ink, not blue-gray shading
BLUE_REACH = 3   # pixels beyond a dark zone within which blue-ink edges are re-blended
INK_BLUE = (30, 170, 230)  # the book's diagram blue, used to re-blend blue-ink edges
MIN_SHARE = 0.005


def brightness(pixel: tuple[int, int, int]) -> int:
    return max(pixel)


def neighbours(x: int, y: int, width: int, height: int) -> list[tuple[int, int]]:
    return [(nx, ny) for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1))
            if 0 <= nx < width and 0 <= ny < height]


def seeds(rgb: Sequence[tuple[int, int, int]], width: int, height: int) -> list[int]:
    """Indexes of every pixel in a connected pure-black area of at least SEED_AREA pixels."""
    seen = bytearray(width * height)
    found: list[int] = []
    for start in range(width * height):
        if seen[start] or brightness(rgb[start]) > LOW:
            continue
        seen[start] = 1
        component = [start]
        queue: deque[int] = deque([start])
        while queue:
            index = queue.popleft()
            for nx, ny in neighbours(index % width, index // width, width, height):
                other = ny * width + nx
                if not seen[other] and brightness(rgb[other]) <= LOW:
                    seen[other] = 1
                    component.append(other)
                    queue.append(other)
        if len(component) >= SEED_AREA:
            found.extend(component)
    return found


def dark_zone(rgb: Sequence[tuple[int, int, int]], width: int, height: int) -> bytearray:
    """Mark pixels reachable from a seed through brightness <= ZONE, then dilate by GROW."""
    mask = bytearray(width * height)
    queue: deque[int] = deque(seeds(rgb, width, height))
    while queue:
        index = queue.popleft()
        if mask[index] or brightness(rgb[index]) > ZONE:
            continue
        mask[index] = 1
        for nx, ny in neighbours(index % width, index // width, width, height):
            if not mask[ny * width + nx]:
                queue.append(ny * width + nx)
    for _ in range(GROW):
        grown = bytearray(mask)
        for index in range(width * height):
            if not mask[index] and any(mask[ny * width + nx] for nx, ny in
                                       neighbours(index % width, index // width, width, height)):
                grown[index] = 1
        mask = grown
    return mask


def grow(mask: bytearray, width: int, height: int, steps: int) -> bytearray:
    """Return mask dilated by steps pixels (4-connected)."""
    for _ in range(steps):
        grown = bytearray(mask)
        for index in range(width * height):
            if not mask[index] and any(mask[ny * width + nx] for nx, ny in
                                       neighbours(index % width, index // width, width, height)):
                grown[index] = 1
        mask = grown
    return mask


def recover(path: Path) -> tuple[Image.Image, Image.Image, float]:
    """Return (original, recovered copy, dark-zone share) for one image."""
    original = Image.open(path).convert("RGB")
    width, height = original.size
    rgb: list[tuple[int, int, int]] = list(original.getdata())
    mask = dark_zone(rgb, width, height)
    near_zone = grow(mask, width, height, BLUE_REACH)
    ink = bytearray(1 if b >= 120 and b - r > CHROMA else 0 for r, _, b in rgb)
    near_ink = grow(ink, width, height, BLUE_REACH)
    out = list(rgb)
    for index, (r, g, b) in enumerate(rgb):
        if not near_zone[index]:
            continue
        value = max(r, g, b)
        if near_ink[index] and b - r >= TINT and b - r >= SATURATION * b and b < INK_BLUE[2]:
            # edge of blue ink drawn over black: re-blend that ink over white instead
            alpha = min(b / INK_BLUE[2], 1.0)
            out[index] = tuple(round(255 * (1 - alpha) + c * alpha) for c in INK_BLUE)
            continue
        if not mask[index] or max(r, g, b) - min(r, g, b) > CHROMA or value > ZONE:
            continue
        level = 255 - round(255 * min(max(value - LOW, 0), HIGH - LOW) / (HIGH - LOW))
        out[index] = (level, level, level)
    recovered = Image.new("RGB", (width, height))
    recovered.putdata(out)
    return original, recovered, sum(mask) / (width * height)


def side_by_side(original: Image.Image, recovered: Image.Image) -> Image.Image:
    gap = 12
    sheet = Image.new("RGB", (original.width * 2 + gap, original.height), (255, 0, 255))
    sheet.paste(original, (0, 0))
    sheet.paste(recovered, (original.width + gap, 0))
    return sheet


def main(argv: Sequence[str]) -> None:
    args = list(argv[1:])
    if len(args) < 2:
        print(__doc__.strip(), file=sys.stderr)
        sys.exit(2)
    out_dir = Path(args.pop(0))
    compare_dir: Path | None = None
    if args and args[0] == "--compare":
        if len(args) < 3:
            print(__doc__.strip(), file=sys.stderr)
            sys.exit(2)
        args.pop(0)
        compare_dir = Path(args.pop(0))
        compare_dir.mkdir(parents=True, exist_ok=True)
    out_dir.mkdir(parents=True, exist_ok=True)
    for name in args:
        path = Path(name)
        original, recovered, share = recover(path)
        if share < MIN_SHARE:
            print(f"native     {path.name}: dark zone {share:.2%}")
            continue
        recovered.save(out_dir / f"{path.stem}.png", optimize=True)
        if compare_dir is not None:
            side_by_side(original, recovered).save(compare_dir / f"{path.stem}.png")
        print(f"recovered  {path.name}: dark zone {share:.1%}")


if __name__ == "__main__":
    main(sys.argv)
