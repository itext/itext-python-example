#!/usr/bin/env bash

SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &>/dev/null && pwd)
shopt -s globstar
for f in "$SCRIPT_DIR"/**/[^_]*.py; do
    echo "Processing $(basename "$(dirname "$f")")/$(basename "$f")..."
    python "$f"
done
