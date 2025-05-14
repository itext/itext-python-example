#!/usr/bin/env bash

SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &>/dev/null && pwd)
find "$SCRIPT_DIR/sandbox" -type f -name '*.py' ! -name '_*' -exec sh -c                  \
    'echo "Processing $(basename "$(dirname "$1")")/$(basename "$1")..." && python "$1"'  \
    find-sh '{}' \;
