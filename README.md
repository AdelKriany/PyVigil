---
<h1>py_file_integrity_checker</h1>

Lightweight CLI tool to create and verify HMAC-based file integrity databases, with optional file encryption (Fernet for small files, AES‑GCM streaming for large files). Password-derived key (Argon2id) secures encryption and HMAC.

<h2>Installation</h2>

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install it.

```bash
git clone https://github.com/AdelKriany/Py_File_Integrity_Checker.git
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
  <div class="warn">
    <ul>
      <li>The encryption key is derived from your password using <strong>Argon2id</strong>. If you forget the password, encrypted files cannot be recovered.</li>
      <li>Use a strong, unique password (≥12 characters).</li>
      <li>Keep the salt file (<code>~/.config/file_integrity_checker/salt</code>) and <code>hash_db.json</code> backed up and secure.</li>
      <li>HMAC uses the derived key; if the password or salt is exposed, integrity and confidentiality are compromised.</li>
      <li>Test encryption/decryption on sample files before running on bulk or important data.</li>
    </ul>
  </div>


<h2>Troubleshooting</h2>
<ol>
    <li>"Salt file not found" — run the initial password setup in the app.</li>
    <li>Permission errors writing salt/config — ensure ~/.config/file_integrity_checker exists and is writable.</li>
    <li>Verification mismatches after changing algorithm — verification uses the DB algorithm; do not change it.</li>
</ol>
