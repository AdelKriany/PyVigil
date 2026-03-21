import os
from argon2.low_level import hash_secret, Type
from argon2 import PasswordHasher
from banner import Colors
import base64
import getpass  

CONFIG_DIR = os.path.expanduser("~/.config/file_integrity_checker")
KEY_PATH = os.path.join(CONFIG_DIR, "secret.key")

def ensure_config_dir():
    os.makedirs(CONFIG_DIR, exist_ok=True)
    os.chmod(CONFIG_DIR, 0o700)

def derive_key_from_password(password: str, salt: bytes = None) -> tuple:
    """
    Derive a 32-byte AES-256 key from a password using Argon2.
    Returns (key, salt) where salt should be stored for future derivations.
    """
    if salt is None:
        salt = os.urandom(16)  # Generate random salt
    
    # Argon2id parameters (balanced between security and speed)
    key_hash = hash_secret(
        password.encode(),
        salt,
        time_cost=2,        # iterations
        memory_cost=65540,  # ~64MB
        parallelism=4,
        type=Type.ID,       # Argon2id
        hash_len=32         # 256-bit key for AES-256
    )
    
    # Convert hash to bytes (take first 32 bytes)
    key = key_hash[:32]
    
    return key, salt

def save_salt(salt: bytes):
    """Save the salt (non-secret) to allow key re-derivation."""
    ensure_config_dir()
    salt_path = os.path.join(CONFIG_DIR, "salt")
    
    with open(salt_path, "wb") as f:
        f.write(salt)
    
    os.chmod(salt_path, 0o644)  
    print(f"{Colors.GREEN}[+] Salt saved at {salt_path}.{Colors.END}")

def load_salt() -> bytes:
    """Load the salt from disk."""
    salt_path = os.path.join(CONFIG_DIR, "salt")
    
    if not os.path.exists(salt_path):
        print(f"{Colors.RED}[X] Salt file not found. Run setup first.{Colors.END}")
        return None
    
    with open(salt_path, "rb") as f:
        return f.read()

def setup_password():
    """
    First-time setup: User creates a password.
    Generates and saves the salt for future key derivations.
    """
    ensure_config_dir()
    
    if os.path.exists(os.path.join(CONFIG_DIR, "salt")):
        print(f"{Colors.YELLOW}[!] Password already configured.{Colors.END}")
        return
    
    print(f"{Colors.CYAN}[*] Setting up password-based encryption...{Colors.END}")
    
    while True:
        password = getpass.getpass("Enter a strong password: ")
        password_confirm = getpass.getpass("Confirm password: ")
        
        if password != password_confirm:
            print(f"{Colors.RED}[X] Passwords do not match. Try again.{Colors.END}")
            continue
        
        if len(password) < 12:
            print(f"{Colors.YELLOW}[!] Password should be at least 12 characters.{Colors.END}")
            continue
        
        break
    
    # Derive key and save salt
    key, salt = derive_key_from_password(password)
    save_salt(salt)
    
    print(f"{Colors.GREEN}[✔] Password configured successfully!{Colors.END}")
    print(f"{Colors.YELLOW}[!] IMPORTANT: Remember this password. If lost, encrypted files cannot be recovered.{Colors.END}")

def get_key_from_password() -> bytes:
    """
    Prompt user for password and derive the encryption key.
    """
    salt = load_salt()
    if salt is None:
        print(f"{Colors.RED}[X] No salt found. Run setup first.{Colors.END}")
        return None
    
    password = getpass.getpass("Enter your password: ")
    key, _ = derive_key_from_password(password, salt)
    
    return key

if __name__ == "__main__":
    import getpass
    ensure_config_dir()
    setup_password()
