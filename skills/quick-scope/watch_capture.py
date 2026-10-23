#!/usr/bin/env python3
"""Wait for complete archived screenshots and return immutable session copies.

Usage: watch_capture.py init|next|ack CAPTURE_DIR SESSION_DIR
"""

import json
import os
from pathlib import Path
import sys
import time


def capture_versions(directory: Path) -> list[str]:
    versions: list[str] = []
    for path in sorted(directory.glob("shot-*.png"), key=lambda item: item.name):
        try:
            stat = path.stat()
        except FileNotFoundError:
            continue
        versions.append(json.dumps([str(path), stat.st_mtime_ns, stat.st_size]))
    return versions


def publish(path: Path, data: bytes) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_bytes(data)
    os.replace(temporary, path)


def main() -> None:
    if len(sys.argv) != 4 or sys.argv[1] not in {"init", "next", "ack"}:
        raise SystemExit(__doc__)
    operation = sys.argv[1]
    captures = Path(sys.argv[2]).resolve()
    session = Path(sys.argv[3]).resolve()
    session.mkdir(parents=True, exist_ok=True)
    state_path = session / "state.json"
    if operation == "init":
        if state_path.exists():
            raise SystemExit("session already initialized; use next")
        captures.mkdir(parents=True, exist_ok=True)
        state = {"seen": capture_versions(captures), "pending": None, "sequence": 0}
        publish(state_path, json.dumps(state).encode())
        return
    state = json.loads(state_path.read_text())
    seen = set(state["seen"])
    pending = state["pending"]
    if operation == "ack":
        if pending is not None:
            state["seen"].append(pending["version"])
            state["pending"] = None
            publish(state_path, json.dumps(state).encode())
        return
    if pending is not None:
        print(pending["path"], flush=True)
        return
    while True:
        for version in capture_versions(captures):
            if version in seen:
                continue
            name, modified, size = json.loads(version)
            path = Path(name)
            try:
                data = path.read_bytes()
                current = path.stat()
            except FileNotFoundError:
                continue
            if (current.st_mtime_ns != modified or current.st_size != size
                    or len(data) != size or not data.startswith(b"\x89PNG\r\n\x1a\n")
                    or not data.endswith(b"\x00\x00\x00\x00IEND\xaeB\x60\x82")):
                continue
            state["sequence"] += 1
            snapshot = session / f"capture-{state['sequence']:06d}.png"
            publish(snapshot, data)
            state["pending"] = {"version": version, "path": str(snapshot)}
            publish(state_path, json.dumps(state).encode())
            print(snapshot, flush=True)
            return
        time.sleep(0.1)


if __name__ == "__main__":
    main()
