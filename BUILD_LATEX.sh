#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "$0")/paper"
for target in supplementary_standalone main; do
  for pass in 1 2 3; do
    pdflatex -interaction=nonstopmode -halt-on-error "$target.tex"
  done
done
