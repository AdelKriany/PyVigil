---
<h1>py_file_integrity_checker</h1>

Lightweight CLI tool to create and verify HMAC-based file integrity databases, with optional file encryption (Fernet for small files, AES‑GCM streaming for large files). Password-derived key (Argon2id) secures encryption and HMAC.

<h2>Installation</h2>

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install it.

```bash
git clone https://github.com/AdelKriany/PyVigil.git
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




<h2>Usage</h2>
<ol>
    <li>
      File Integrity Checker (Initialize or Verify)
      <ul>
        <li><strong>Initialize:</strong> choose a hashing algorithm (e.g., sha256), optionally encrypt files, and create <code>hash_db.json</code>.</li>
        <li><strong>Verify:</strong> compare filesystem against <code>hash_db.json</code> (reports deleted/modified/new/ok).</li>
      </ul>
    </li>
    <li>
      Encrypt a File/Directory (encrypts files using your password-derived key)
    </li>
    <li>
      Decrypt a File/Directory (prompts for your password)
    </li>
    <li>
      Exit
    </li>
  </ol>
  
Examples:

  <h1>File Integrity Checker — Quick Instructions</h1>

  <h2>Initialize (create SHA-256 DB, no encryption)</h2>
  <ol>
    <li>Choose option <code>1</code></li>
    <li>Enter the directory path</li>
    <li>Choose algorithm: <code>sha256</code></li>
    <li>Encrypt? <code>no</code></li>
    <li>Initialize DB? <code>yes</code></li>
  </ol>
  <p>Result: creates <code>hash_db.json</code> in the target location (algorithm stored in DB).</p>

  <h2>Verify later (compare filesystem to DB)</h2>
  <ol>
    <li>Choose option <code>1</code></li>
    <li>Enter the same directory path</li>
    <li>The tool will read the algorithm from <code>hash_db.json</code></li>
    <li>Initialize DB? <code>no</code></li>
  </ol>
  <p>Result: reports files as <strong>deleted / modified / new / ok</strong>.</p>

   <h2>Security &amp; Important Warnings</h2>
  ## 🛡️ Security Model & Architecture

This tool is designed with a "Security-First" mindset, ensuring both confidentiality and data integrity through modern cryptographic primitives.

### 🔐 Cryptographic Specifications
| Feature | Implementation |
| :--- | :--- |
| **Key Derivation (KDF)** | **Argon2id** (Type: 2, Version: 19) |
| **Small File Encryption** | **Fernet** (AES-128-CBC + HMAC-SHA256) |
| **Large File Encryption** | **AES-256-GCM** (Authenticated Streaming) |
| **Integrity Hashing** | User-defined (SHA-256, SHA-512, etc.) + HMAC |

### ⚠️ Important Warnings
> [!IMPORTANT]
> **Zero-Knowledge Design**: The application never stores your plaintext password. The encryption key is derived on-the-fly.

* **Password Recovery**: If you forget your password, the encrypted files **cannot be recovered**. There is no "backdoor."
* **Salt Portability**: The encryption relies on the salt file located at `~/.config/file_integrity_checker/salt`. If you move your encrypted files to another machine, you **must** also move the salt file.
* **Key Strength**: Always use a strong, unique password (minimum 12+ characters) to maximize the effectiveness of Argon2id.
* **Data Integrity**: HMAC is used to verify that your files haven't been tampered with. If the password or salt is compromised, the integrity guarantee is void.
  

<h2>Troubleshooting</h2>
<ol>
    <li>"Salt file not found" — run the initial password setup in the app.</li>
    <li>Permission errors writing salt/config — ensure ~/.config/file_integrity_checker exists and is writable.</li>
    <li>Verification mismatches after changing algorithm — verification uses the DB algorithm; do not change it.</li>
</ol>
