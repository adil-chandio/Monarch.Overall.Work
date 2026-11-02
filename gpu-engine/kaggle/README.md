# MONARCH® Zero-Budget Kaggle Dual T4 (`GPU T4 x2`) Engine

## Safe GitHub Secrets Setup (Never paste keys in chat)
In your GitHub repository (`Settings -> Secrets and variables -> Actions -> New repository secret`), add:
1. `KAGGLE_USERNAME` — your Kaggle username
2. `KAGGLE_API_TOKEN` — your `KGAT_...` token from Kaggle (`Settings -> Account -> API -> Create New Token`)

## Why `machine_shape: "NvidiaTeslaT4"` Matters
Setting `"enable_gpu": true` alone defaults CLI kernels onto legacy `P100`. Including `"machine_shape": "NvidiaTeslaT4"` in `kernel-metadata.json` allocates **GPU T4 x2 (`2 x 16GB = 32GB VRAM`)** with 30 free GPU hours every week and zero credit card required.
