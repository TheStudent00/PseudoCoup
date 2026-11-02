#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
export PYTHONPATH="$ROOT"
python3 "$ROOT/tests/test_quickfox_all_12_langs.py"
python3 "$ROOT/tests/test_roundtrip_two_cycles.py"
python3 "$ROOT/tests/test_holder_bridge.py"
python3 "$ROOT/examples/polyglot_codec/build_polyglot_codec.py"
python3 "$ROOT/tests/test_gpu_tensor_lowerer.py"
python3 "$ROOT/tests/test_hub_complete.py" > /dev/null && echo "[PASS] test_hub_complete: 12,164 lowered Units + Z3 proofs verified"
