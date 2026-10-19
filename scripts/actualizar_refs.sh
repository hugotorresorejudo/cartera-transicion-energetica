#!/bin/sh
# Regenera supuestos, fusiona referencias.yaml (+ .json) y la documentación del método.
set -e
cd "$(dirname "$0")/.."
python scripts/gen_supuestos.py
python scripts/merge_refs.py
python scripts/build_metodo.py
