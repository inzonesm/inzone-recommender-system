# Conda Environment Setup

## Quick Start

1. **Activate the environment:**
   ```bash
   conda activate gorse
   ```

2. **Run the sync script:**
   ```bash
   python sync_firestore_to_gorse.py
   ```

3. **Deactivate when done:**
   ```bash
   conda deactivate
   ```

## Environment Details

- **Name:** gorse
- **Python Version:** 3.11
- **Location:** `/home/yxydw-24-04/anaconda3/envs/gorse`

## Installed Packages

- requests
- firebase-admin (includes Firestore client)

## Verify Installation

```bash
conda activate gorse
python -c "import requests; import firebase_admin; print('All packages installed!')"
```

## Add More Packages

```bash
conda activate gorse
pip install <package_name>
```

## Delete Environment (if needed)

```bash
conda deactivate
conda env remove -n gorse
```
