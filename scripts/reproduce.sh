#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
python3 scripts/audit_results.py
python3 scripts/check_release.py
python3 scripts/render_result_figures.py
