#py_file_integrity_checker

Lightweight CLI tool to create and verify HMAC-based file integrity databases, with optional file encryption (Fernet for small files, AES‑GCM streaming for large files). Password-derived key (Argon2id) secures encryption and HMAC.

##Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install it.

```bash
git clone <repo-url>
cd py_file_integrity_checker
python -m venv .venv
source .venv/bin/activate   # Linux/macOS
.venv\Scripts\activate      # Windows
pip install --upgrade pip
pip install cryptography argon2-cffi tqdm
chmod +x main.py
```

##run the app
```python
python main.py
```

On first run you'll be prompted to configure a password used to derive the encryption key. The salt is stored at ~/.config/file_integrity_checker/salt




##Usage

1 — File Integrity Checker (Initialize or Verify)
    Initialize: choose a hashing algorithm (e.g., sha256), optionally encrypt files, and create hash_db.json.
    Verify: compare filesystem against hash_db.json (reports deleted/modified/new/ok).
2 — Encrypt a File/Directory (encrypts files using your password-derived key).
3 — Decrypt a File/Directory (prompts for your password).
4 — Exit
Examples:

Initialize a directory with SHA-256 and no encryption: choose option 1 → path → sha256 → no for encrypt → yes to initialize DB.
Verify later: option 1 → same path → algorithm will be read from DB → choose no for initialization to run verification.


#Security & important warnings
The encryption key is derived from your password using Argon2id. If you forget the password, encrypted files cannot be recovered.

Use a strong, unique password (≥12 characters).
Keep the salt file (~/.config/file_integrity_checker/salt) and hash_db.json safe and backed up if you need to move/recover files.
HMAC uses the derived key; exposure of the password or salt defeats integrity and confidentiality guarantees.
Test encryption/decryption on sample files before bulk operations.