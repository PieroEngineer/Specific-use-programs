import paramiko
import os
import sys
from pathlib import Path

# ========================= CONFIGURATION =========================

HOST = "10.125.8.6"
PORT = 22
USERNAME = "USERNAME"               
PASSWORD = "PASSWORD"           # Only for testing
PRIVATE_KEY_PATH = None

# Local folder (Linux side) that contains the files you want to send
LOCAL_FOLDER = r"local_folder"     # ← change to your real source folder on Linux later

# Remote folder on Windows (where files will arrive)
REMOTE_FOLDER = "."

# =================================================================

def upload_dir(sftp, local_dir, remote_dir):
    """Recursive upload of entire directory"""
    Path(local_dir).mkdir(parents=True, exist_ok=True)
    
    for item in os.listdir(local_dir):
        local_path = os.path.join(local_dir, item)
        remote_path = remote_dir + "/" + item if remote_dir != "/" else "/" + item
        
        if os.path.isdir(local_path):
            try:
                sftp.mkdir(remote_path)
            except IOError:
                pass  # directory probably already exists
            upload_dir(sftp, local_path, remote_path)
        else:
            print(f"Uploading {local_path} → {remote_path}")
            sftp.put(local_path, remote_path)

def main():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        if PRIVATE_KEY_PATH:
            key = paramiko.Ed25519Key(filename=PRIVATE_KEY_PATH)  # or RSAKey
            ssh.connect(hostname=HOST, port=PORT, username=USERNAME, pkey=key)
        else:
            ssh.connect(hostname=HOST, port=PORT, username=USERNAME, password=PASSWORD)
        
        sftp = ssh.open_sftp()
        #sftp.chdir(REMOTE_FOLDER)  # go to the destination folder
        sftp.chdir(".")     # CoreFTP already puts us in the home directory

        #upload_dir(sftp, LOCAL_FOLDER, REMOTE_FOLDER)
        upload_dir(sftp, LOCAL_FOLDER, ".")
        
        sftp.close()
        ssh.close()
        print("¡Transfer completed successfully!")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":

    main()
