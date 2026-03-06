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


#3. encrypt a file using AES-GCM (streaming mode)
def encrypt_file(file_path):
    key = load_key()
    nonce = os.urandom(12)

    cipher = Cipher(
        algorithms.AES(key),
        modes.GCM(nonce),
    )
    encryptor = cipher.encryptor()

    file_size = os.path.getsize(file_path)
    output_path = file_path + ".tmp"

    with open(file_path, "rb") as f_in, open(output_path, "wb") as f_out:
        
        # Write header (mode)
        f_out.write(b"S")

        # Write nonce
        f_out.write(nonce)

        with tqdm(total=file_size, unit='B', unit_scale=True, desc="Encrypting") as pbar:
            while True:
                chunk = f_in.read(CHUNK_SIZE)
                if not chunk:
                    break

                encrypted_chunk = encryptor.update(chunk)
                f_out.write(encrypted_chunk)

                pbar.update(len(chunk))

            encryptor.finalize()

        # Write authentication tag
        f_out.write(encryptor.tag)

    os.replace(output_path, file_path)

    print(f"\n{Colors.GREEN}[✔] File {file_path} has been ENCRYPTED (AES-GCM streaming).{Colors.END}")



# # 3. Encrypt a file
# def encrypt_file(file_path):
#     raw_key=open('secret.key', 'rb').read()
#     aesgcm=AESGCM(raw_key)
#     nonce=os.urandom(12)

#     file_size=os.path.getsize(file_path)
#     output_path=file_path+'.tmp'


#     with open(file_path, 'rb') as f_in, open(output_path, 'wb') as f_out:
#         f_out.write(nonce)  # Write nonce at the beginning
#         with tqdm(total=file_size, unit='B', unit_scale=True, desc=f"Encrypting")as pbar:
#             data=f_in.read()
#             encrypted = aesgcm.encrypt(nonce, data, None)
#             f_out.write(encrypted)
#             pbar.update(file_size)
#     os.replace(output_path, file_path)
#     print(f"\n{Colors.GREEN}[✔] File {file_path} has been ENCRYPTED.{Colors.END}")

    # key = load_key()
    # if not key: return
    # f = Fernet(key)
  
    # file_size = os.path.getsize(file_path)
    
    # # Fernet لا يدعم التشفير على أجزاء (Streaming) بشكل مباشر بسهولة، 
    # # لذا سنستخدم tqdm لإظهار حالة القراءة والمعالجة
    # with tqdm(total=file_size, unit='B', unit_scale=True, desc=f"Encrypting {os.path.basename(file_path)}") as pbar:
    #     with open(file_path, "rb") as file:
    #         file_data = file.read()
    #         pbar.update(file_size) # تحديث الشريط بعد القراءة
    
    # encrypted_data = f.encrypt(file_data)
    
    # with open(file_path, "wb") as file:
    #     file.write(encrypted_data)
    # print(f"\n{Colors.GREEN}[✔] File {file_path} has been ENCRYPTED.{Colors.END}")







"""# 4. Decrypt a file fix it later """
# # 4. Decrypt a file
# def decrypt_file(file_path):
#    # secret_key_check=getpass.getpass(f"{Colors.YELLOW}Enter the secret key to decrypt the file: {Colors.END}").strip().encode('utf-8')
#     key = open("secret.key", "rb").read()
#     nonce = os.urandom(12)

#     # key = secret_key_check
   
#     # f = Fernet(key)
#     with open(file_path, "rb") as f_in, open(output_path, "wb") as f_out:
#         f_out.write(nonce)
#         with tqdm(total=file_size, unit='B', unit_scale=True, desc="Encrypting") as pbar:
#             while True:
#                 chunk = f_in.read(CHUNK_SIZE)
#                 if not chunk:
#                     break
#                 encrypted_chunk = encryptor.update(chunk)
#                 f_out.write(encrypted_chunk)
#                 pbar.update(len(chunk))

#     decryptor.finalize()



#     with open(file_path, "rb") as file:
#         encrypted_data = file.read()
    
#     try:
#         decrypted_data = f.decrypt(encrypted_data)
#         with open(file_path, "wb") as file:
#             file.write(decrypted_data)
#         print(f"[!] File {file_path} has been DECRYPTED.")
#     except Exception:
#         print("[X] Invalid Key or file is not encrypted.")



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