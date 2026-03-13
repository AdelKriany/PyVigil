#!/usr/bin/env python3
import hashlib
import os
import json
import sys
import getpass
from tqdm import tqdm
from cryptography.fernet import Fernet
from cryp import load_key, encrypt_file, decrypt_file, decrypt_path
import hmac
import getpass  
from key import setup_password, ensure_config_dir, load_salt
from banner import print_banner, Colors

 
def print_security_warning():
    """Display security warning on first setup."""
    print(f"""
{Colors.RED}
╔════════════════════════════════════════════════════════════════╗
║                    ⚠️  SECURITY WARNING  ⚠️                    ║
╠════════════════════════════════════════════════════════════════╣
║ Your encryption key is derived from your password.             ║
║                                                                ║
║ • If you forget your password, encrypted files CANNOT be      ║
║   recovered. There is no "forgot password" option.            ║
║                                                                ║
║ • Use a STRONG, UNIQUE password (12+ characters).             ║
║                                                                ║
║ • Do NOT share your password with anyone.                     ║
╚════════════════════════════════════════════════════════════════╝
{Colors.END}
    """)


def Hashing_engine(file_path, algorithm):
    """
    Computes the hash of a file using the specified algorithm.
    Supported: 'md5', 'sha1', 'sha256', 'sha512', etc.
    Uses HMAC with the encryption key for integrity verification.
    """
    key = load_key()
    hash_algorithm = hmac.new(key, digestmod=algorithm)
    
    try:
        with open(file_path, 'rb') as f:
            file_size = os.path.getsize(file_path)
            with tqdm(total=file_size, unit='B', unit_scale=True, desc=f"Hashing {os.path.basename(file_path)[:20]}") as pbar:
                for bite_block in iter(lambda: f.read(4096), b""):  
                    hash_algorithm.update(bite_block)
                    pbar.update(len(bite_block))
        return hash_algorithm.hexdigest()
    except Exception as e:
        print(f"{Colors.RED}[X] Error hashing file {file_path}: {e}{Colors.END}")
        return None


def verify_directory(directory_path, stored_data, hash_ask):
    """
    Verify all files in a directory against stored hashes.
    Reports: DELETED, MODIFIED, OK, and NEW FILES.
    """
    # Check files that exist in the database
    for stored_path, file_data in stored_data["files"].items():
        if not os.path.exists(stored_path):
            print(f"{Colors.RED}[DELETED]: {Colors.END}{stored_path}")
            continue

        current_hash = Hashing_engine(stored_path, hash_ask)
        if current_hash is None:
            continue

        if current_hash != file_data["hash"]:
            print(f"{Colors.RED}[MODIFIED]: {Colors.END}{stored_path}")
        else:
            status = "ENCRYPTED" if file_data.get("is_encrypted", False) else "(plaintext)"
            print(f"{Colors.GREEN}[OK] {status}: {Colors.END}{stored_path}")

    # Search for new files
    for root, dirs, files in os.walk(directory_path):
        for file in files:
            full_path = os.path.join(root, file)
            if full_path not in stored_data["files"]:
                print(f"{Colors.YELLOW}[NEW FILE]: {Colors.END}{full_path}")


def main_hash():
    """
    Main hash function that initializes or verifies file integrity.
    Supports encryption and hashing in one workflow.
    """
    # Get target path
    target_path = input(f"{Colors.YELLOW}Enter path (file or directory): {Colors.END}").strip()
    if not os.path.exists(target_path):
        print(f"{Colors.RED}[!] Path does not exist{Colors.END}")
        return
    
    # Choose hashing algorithm
    hash_ask = input("Which hashing algorithm do you want to use? (e.g., md5, sha1, sha256, sha512): ").strip().lower()
    if not hasattr(hashlib, hash_ask):
        print(f"{Colors.RED}[!] Unsupported hashing algorithm: {hash_ask}{Colors.END}")
        return
    
    db_json = "hash_db.json"

    # Ask about encryption
    crypt_choice = input(f"{Colors.YELLOW}Do you want to encrypt the files? (yes/no): {Colors.END}").strip().lower()
    is_encrypted = False
    
    if crypt_choice == "yes":
        print(f"{Colors.CYAN}[*] Encrypting files...{Colors.END}")
        if os.path.isfile(target_path):
            encrypt_file(target_path)
            is_encrypted = True
        elif os.path.isdir(target_path):
            for root, dirs, files in os.walk(target_path):
                for file in files:
                    full_path = os.path.join(root, file)
                    encrypt_file(full_path)
            is_encrypted = True
        print(f"{Colors.GREEN}[✔] Encryption complete. Now generating integrity hashes...{Colors.END}")

    # Settings session
    print(f"\n{Colors.MAGENTA}--- SETTINGS ---{Colors.END}")
    re_init = input("Initialize new database? (yes/no): ").strip().lower()
    
    if re_init == "yes":
        # Create new database with hashes
        db_data = {
            "metadata": {
                "algorithm": hash_ask,
                "version": "2.0",
            },
            "files": {}
        }

        if os.path.isdir(target_path):
            for root, dirs, files in os.walk(target_path):
                for file in files:
                    full_path = os.path.join(root, file)
                    file_hash = Hashing_engine(full_path, hash_ask)
                    if file_hash:
                        db_data["files"][full_path] = {
                            "hash": file_hash,
                            "is_encrypted": (crypt_choice == "yes")
                        }
        else:
            file_hash = Hashing_engine(target_path, hash_ask)
            if file_hash:
                db_data["files"][target_path] = {
                    "hash": file_hash,
                    "is_encrypted": (crypt_choice == "yes")
                }

        # Write database
        with open(db_json, 'w') as f:
            json.dump(db_data, f, indent=4)
        print(f"{Colors.GREEN}[✔] Database initialized!{Colors.END}")
   
    elif re_init == "no":
        # Verify against existing database
        if not os.path.exists(db_json):
            print(f"{Colors.RED}[!] No database found. Run with 'Initialize new database' first.{Colors.END}")
            return

        with open(db_json, 'r') as f:
            stored = json.load(f)
        
        alg_used = stored.get("metadata", {}).get("algorithm", hash_ask) 
        print(f"\n{Colors.CYAN}[*] Checking integrity using {alg_used.upper()}...{Colors.END}\n")
        
        # Verify files
        if os.path.isdir(target_path):
            verify_directory(target_path, stored, alg_used) 
        else:
            # Single file verification
            for f_path, file_data in stored["files"].items():
                if not os.path.exists(f_path):
                    print(f"{Colors.RED}[DELETED]: {Colors.END}{f_path}")
                    continue
                
                curr_h = Hashing_engine(f_path, algorithm=alg_used)
                if curr_h is None:
                    continue
                
                old_h = file_data.get("hash")
                if curr_h != old_h:
                    print(f"{Colors.RED}[MODIFIED]: {Colors.END}{f_path}")
                else:
                    status = "ENCRYPTED" if file_data.get("is_encrypted", False) else "(plaintext)"
                    print(f"{Colors.GREEN}[OK] {status}: {Colors.END}{f_path}")
    else:
        print(f"{Colors.RED}[!] Invalid option.{Colors.END}")


def main_menu():
    """Main menu for the file integrity checker."""
    print_banner()
    
    print(f"{Colors.MAGENTA}--- CONTROL PANEL ---{Colors.END}")
    print("1. File Integrity Checker (Initialize or Verify)")
    print("2. Encrypt a File/Directory")
    print("3. Decrypt a File/Directory")
    print("4. Exit")
    
    choice = input(f"\n{Colors.YELLOW}Select an option (1-4): {Colors.END}").strip()

    if choice == "1":
        main_hash()
    
    elif choice == "2":
        path_to_encrypt = input(f"{Colors.YELLOW}Enter path (file or directory): {Colors.END}").strip()
        if os.path.exists(path_to_encrypt):
            if os.path.isfile(path_to_encrypt):
                encrypt_file(path_to_encrypt)
            elif os.path.isdir(path_to_encrypt):
                print(f"{Colors.CYAN}[*] Encrypting directory...{Colors.END}")
                for root, dirs, files in os.walk(path_to_encrypt):
                    for file in files:
                        full_path = os.path.join(root, file)
                        encrypt_file(full_path)
                print(f"{Colors.GREEN}[✔] Directory encrypted!{Colors.END}")
        else:
            print(f"{Colors.RED}[!] Path does not exist{Colors.END}")

    elif choice == "3": 
        path_to_decrypt = input(f"{Colors.YELLOW}Enter path (file or directory): {Colors.END}").strip()
        if os.path.exists(path_to_decrypt):
            decrypt_path(path_to_decrypt)
        else:
            print(f"{Colors.RED}[!] Path does not exist{Colors.END}")

    elif choice == "4":
        print(f"{Colors.GREEN}[✔] Goodbye!{Colors.END}")
        sys.exit(0)

    else:
        print(f"{Colors.RED}[!] Invalid option.{Colors.END}")


def init_app():
    """Initialize the application on first run."""
    ensure_config_dir()
    
    # Check if password is already set up
    if load_salt() is None:
        print_security_warning()
        setup_password()
    
    main_menu()


if __name__ == "__main__":
    try:
        init_app()
    except KeyboardInterrupt:
        print(f"\n{Colors.RED}[X] Interrupted by user. Exiting...{Colors.END}")
        sys.exit(0)
    except EOFError:
        print(f"\n{Colors.GREEN}[✔] Exiting program. Goodbye!{Colors.END}")
        sys.exit(0)
    except Exception as e:
        print(f"{Colors.RED}[X] Unexpected error: {e}{Colors.END}")
        sys.exit(1)
