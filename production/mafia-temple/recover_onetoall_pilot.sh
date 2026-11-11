#!/usr/bin/env bash
# Recover the already-completed private Kaggle job; never starts another run.
set -euo pipefail
: "${KAGGLE_USERNAME:?Kaggle username required}"
python production/mafia-temple/recover_onetoall_files.py
