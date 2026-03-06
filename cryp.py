import os
from cryptography.fernet import Fernet
import json
import sys
from tqdm import tqdm
import getpass
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import base64

# This file contains the core cryptographic functions for key generation, encryption, and decryption.
CHUNK_SIZE = 1024 * 1024  # 1MB per chunk


# i will put this on the another file later 
class Colors:
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'


# 1. Generate and save a key (Do this only once!)
def generate_key():
    key=os.urandom(32)  # AES-256 key
    with open("secret.key", "wb") as key_file:
        key_file.write(key)
    print("[+] Key generated and saved as 'secret.key'. Keep it safe!")

# 2. Load the existing key
def load_key():
    return open("secret.key", "rb").read()



def update_encryption_status(file_path):
    db_json = "hash_db.json"

    if not os.path.exists(db_json):
        return

    with open(db_json, "r") as f:
        data = json.load(f)

    if file_path in data["files"]:
        data["files"][file_path]["is_encrypted"] = True

    with open(db_json, "w") as f:
        json.dump(data, f, indent=4)



def encrypt_file(file_path):
    key = load_key() # Assuming you have a function to load the key
    file_size = os.path.getsize(file_path)
    
    # Define a threshold (e.g., 50MB) to decide between Fernet and GCM
    # Adjust this based on your performance needs
    FERNET_THRESHOLD = 50 * 1024 * 1024 

    # --- MODE: FERNET ---
    if file_size < FERNET_THRESHOLD:
        with open(file_path, "rb") as f:
            data = f.read()
        
        fernet_key = base64.urlsafe_b64encode(key)
        f = Fernet(fernet_key)
        encrypted_data = f.encrypt(data)
        
        with open(file_path, "wb") as f_out:
            f_out.write(b"F") # Header
            f_out.write(encrypted_data)
        print(f"{Colors.GREEN}[✔] File {file_path} encrypted using Fernet.{Colors.END}")

    # --- MODE: AES-GCM ---
    else:
        nonce = os.urandom(12)
        cipher = Cipher(algorithms.AES(key), modes.GCM(nonce))
        encryptor = cipher.encryptor()
        
        output_path = file_path + ".tmp_enc"
        
        with open(file_path, "rb") as f_in, open(output_path, "wb") as f_out:
            # Write header 'S' and the 12-byte nonce
            f_out.write(b"S")
            f_out.write(nonce)
            
            with tqdm(total=file_size, unit='B', unit_scale=True, desc="Encrypting") as pbar:
                while True:
                    chunk = f_in.read(CHUNK_SIZE)
                    if not chunk: break
                    f_out.write(encryptor.update(chunk))
                    pbar.update(len(chunk))
                
                encryptor.finalize()
                f_out.write(encryptor.tag) # Append 16-byte tag
        
        os.replace(output_path, file_path)
        print(f"\n{Colors.CYAN}[✔] File {file_path} encrypted using AES-GCM.{Colors.END}")
        update_encryption_status(target_path)
        return True



def decrypt_file(file_path):
    key = load_key()
    file_size = os.path.getsize(file_path)
    
    if file_size < 1:
        print(f"{Colors.RED}[X] File is empty.{Colors.END}")
        return

    with open(file_path, "rb") as f_in:
        # 1. Read the first byte to determine the encryption mode
        mode = f_in.read(1)
        
        # --- MODE: FERNET (Small Files) ---
        if mode == b"F":
            # Fernet needs a base64 encoded version of your 32-byte key
            fernet_key = base64.urlsafe_b64encode(key)
            f = Fernet(fernet_key)
            encrypted_data = f_in.read()
            
            try:
                decrypted_data = f.decrypt(encrypted_data)
                with open(file_path, "wb") as f_out:
                    f_out.write(decrypted_data)
                print(f"{Colors.GREEN}[✔] File {file_path} decrypted using Fernet.{Colors.END}")
            except Exception:
                print(f"{Colors.RED}[X] Fernet decryption failed. Invalid key or corrupted data.{Colors.END}")

        # --- MODE: AES-GCM (Large/Streaming Files) ---
        elif mode == b"S":
            # Read the 12-byte nonce immediately after the mode byte
            nonce = f_in.read(12)
            
            # The 16-byte tag is at the very end of the file
            f_in.seek(-16, os.SEEK_END)
            tag = f_in.read(16)
            
            # Actual encrypted data is between the nonce and the tag
            f_in.seek(1 + 12) # Skip mode (1) and nonce (12)
            data_size = file_size - 1 - 12 - 16
            
            cipher = Cipher(algorithms.AES(key), modes.GCM(nonce, tag))
            decryptor = cipher.decryptor()
            
            output_path = file_path + ".tmp_dec"
            try:
                with open(output_path, "wb") as f_out:
                    with tqdm(total=data_size, unit='B', unit_scale=True, desc="Decrypting") as pbar:
                        remaining = data_size
                        while remaining > 0:
                            chunk = f_in.read(min(CHUNK_SIZE, remaining))
                            if not chunk: break
                            f_out.write(decryptor.update(chunk))
                            remaining -= len(chunk)
                            pbar.update(len(chunk))
                        
                        decryptor.finalize()
                
                os.replace(output_path, file_path)
                print(f"\n{Colors.CYAN}[✔] File {file_path} decrypted using AES-GCM.{Colors.END}")
            except Exception as e:
                if os.path.exists(output_path): os.remove(output_path)
                print(f"\n{Colors.RED}[X] GCM Decryption failed: {e}{Colors.END}")
        
        else:
            print(f"{Colors.YELLOW}[!] File does not have a valid encryption header (F/S).{Colors.END}")