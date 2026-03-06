#!/usr/bin/env python3
import hashlib
import os
import json
import sys
from tqdm import tqdm
from cryptography.fernet import Fernet# next version remove fernet
from cryp import generate_key, load_key, encrypt_file, decrypt_file
import hmac
import getpass

"""colors for the panel"""
class Colors:
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_banner():
    """Displays a cool ASCII banner at startup."""
    banner = f"""
{Colors.CYAN}{Colors.BOLD}
    ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
    ┃      FILE INTEGRITY CHECKER & BUILDER          ┃
    ┃            Version 2.0 | By Adel               ┃
    ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
{Colors.END}"""
    print(banner)
""""""


 
def Hashing_engine(file_path,algorithm):
    """
    Computes the hash of a file using the specified algorithm.
    Supported: 'md5', 'sha1', 'sha256', 'sha512', etc.
    """
    #sha256_hash = hashlib.sha256()
    # hash_algorithm = hashlib.new(algorithm)
    key=load_key()
    hash_algorithm = hmac.new(key, digestmod=algorithm)
    try:
        with open(file_path, 'rb') as f:
            file_size = os.path.getsize(file_path)
            with tqdm(total=file_size, unit='B', unit_scale=True, desc=f"Hashing {os.path.basename(file_path)[:20]}") as pbar:
                 for bite_block in iter(lambda: f.read(4096), b""):   
                     # print(f"I am hashing this data: {bite_block.strip()}")#if had any problem remove the strip
                     hash_algorithm.update(bite_block)
                     pbar.update(len(bite_block))
        # incorporate the secret key into the final hash
       # hash_algorithm.update(secret_salt.encode())
        return hash_algorithm.hexdigest()
    except Exception as e:
        print(f"Error hashing file {file_path}: {e}")
        return None

# not clear yet
def main_hash():
    """main hash function that suppose to choose the type of hash 
    and re-initialize the old one and the check if the hash was changed 
    """
    # enter the full path of the file/log with the name of the file/log
    target_path = input(f"{Colors.YELLOW}Enter path:{Colors.END}").strip()
    if not os.path.exists(target_path):
        print(f"{Colors.RED}[!]Path does not exist{Colors.END}")
        exit(-1)
    # ask user which hash algo to use
    hash_ask=input("Which hashing algorithm do you want to use? (e.g., md5, sha1, sha256, sha512): ").strip().lower()
    if not hasattr(hashlib, hash_ask):
        print(f"Unsupported hashing algorithm: {hash_ask}")
        exit(-1)
    
    # create a file that save the hash file
    db_json = "hash_db.json"

    # encrypt after hash
    crypt_choice = input(f"{Colors.YELLOW}Do you want to encrypt the files after hashing? (yay/nay):{Colors.END} ").strip().lower()################

    if crypt_choice=="yay":
        encrypt_file(target_path)
    

# setting session
    print(f"\n{Colors.MAGENTA}--- SETTINGS ---{Colors.END}")

    re_init = input("re-initialize? (yay/nay): ").strip().lower()
    
    if re_init == "yay":#create metadata for storing it in the hash_db.json
        db_data={
            "metadata":{
                "algorithm": hash_ask,
                "version": "2.0",
            },
            "files": {}
        }
        ######later
        if os.path.isdir(target_path):
            for root, dirs, files in os.walk(target_path):
                for file in files:
                    full_path = os.path.join(root, file)
                    db_data["files"][full_path]= Hashing_engine(full_path, hash_ask)
        else:
            db_data["files"][target_path]= Hashing_engine(target_path, hash_ask)
        ######later

        #write a the hash details into the file db_jsofile
        with open(db_json, 'w') as f:
            json.dump(db_data, f, indent=4)
        print(f"{Colors.GREEN}[✔]Database updated!{Colors.END}")
   
    else:#re_init == "nay"
        if not os.path.exists(db_json):
            print(f"{Colors.RED}[!] No DB found{Colors.END}")
            exit(-1)
        #reload all the stored data on db_json into stored var
        with open(db_json, 'r') as f:
            stored = json.load(f)
        
        # define what algo we used in metadata
        alg_used = stored.get("metadata", {}).get("algorithm", hash_ask) 
        print(f"\n{Colors.CYAN}[*] Checking integrity using {alg_used.upper()}...{Colors.END}\n")
        
        #see if the hash was changed or not 
        for f_path, old_h in stored["files"].items(): 
            curr_h = Hashing_engine(f_path,algorithm=alg_used)
            if curr_h != old_h:
                print(f"{Colors.RED}[MODIFIED]: {Colors.END}{f_path}")
            else:
                print(f"{Colors.GREEN}[SAVE]: {Colors.END}{f_path}")


#main functioin for choising 
def main_menu():
    print_banner()
    #input session
    print(f"{Colors.MAGENTA}--- CONTROL PANEL ---{Colors.END}")
    print("1. file Integrity checker (checker/verify) - file Integrity builder (builder/init)")
    print("2. Encrypt a File")
    print("3. Decrypt a File")
    print("4. Generate New Key (Careful!)")
    choice = input(f"\n{Colors.YELLOW}Select an option (1-4): {Colors.END}").strip()

    if choice == "1":
        main_hash()
    # Encrypt choise
    elif choice == "2":
        file_to_encrypt = input(f"{Colors.YELLOW}Enter the path of the file to encrypt: {Colors.END}").strip()
        if os.path.exists(file_to_encrypt):
            encrypt_file(file_to_encrypt)

        else:
            print(f"{Colors.RED}[!] File does not exist{Colors.END}")

    elif choice == "3": 
        file_to_decrypt = input(f"{Colors.YELLOW}Enter the path of the file to decrypt: {Colors.END}").strip()
        if os.path.exists(file_to_decrypt):
            decrypt_file(file_to_decrypt)

        else:
            print(f"{Colors.RED}[!] File does not exist{Colors.END}")

    elif choice == "4":
        confirm = input(f"{Colors.RED}This will overwrite your existing key and you may lose access to encrypted files. Are you sure? (yes/no): {Colors.END}").strip().lower()
        if confirm == "yes":
            generate_key()

        else:
            print(f"{Colors.GREEN}[✔] Key generation cancelled.{Colors.END}")

    else:
        print(f"{Colors.RED}[!] Invalid option. Exiting.{Colors.END}")
        exit(-1)

#main 
if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        print(f"\n{Colors.RED}[X] Interrupted by user. Exiting...{Colors.END}")
        sys.exit(0)
    except EOFError :
         print(f"\n{Colors.GREEN}[✔] Exiting program (Ctrl+D). Goodbye!{Colors.END}")
         sys.exit(0)