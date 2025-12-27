# Mini Project: SFTP File Transfer Utility

This mini project provides a Python script to **upload files or entire directories via SFTP** from a Linux machine to a remote Windows server using **Paramiko**.

Main script:
- **`sending_via_sftp.py`** – Establishes an SSH connection, opens an SFTP session, and recursively uploads all files from a local folder to a remote folder.

---

## What the script does

1. **Configuration**
   - Set `HOST`, `PORT`, `USERNAME`, and either `PASSWORD` or `PRIVATE_KEY_PATH`.
   - Define `LOCAL_FOLDER` (source directory) and `REMOTE_FOLDER` (destination directory).

2. **Connection**
   - Uses `paramiko.SSHClient` to connect to the remote host.
   - Supports password or private key authentication.

3. **Upload**
   - Recursively uploads all files and subfolders from `LOCAL_FOLDER` to `REMOTE_FOLDER`.
   - Creates remote directories if they do not exist.

4. **Logging**
   - Prints each file being uploaded and a success message when done.

---

## Inputs & Outputs
- **Input:** Local folder path containing files to send.
- **Output:** Files uploaded to the remote folder via SFTP.

---

## Quick start

1. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # macOS/Linux
.venv\\Scripts\\activate     # Windows
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Edit configuration in `sending_via_sftp.py`:
```python
HOST = "your.server.ip"
PORT = 22
USERNAME = "your_username"
PASSWORD = "your_password"  # or set PRIVATE_KEY_PATH for key-based auth
LOCAL_FOLDER = r"/path/to/local/folder"
REMOTE_FOLDER = "/remote/path"
```

4. Run the script:
```bash
python sending_via_sftp.py
```

---

## Security notes
- Avoid hardcoding passwords in production; use environment variables or a secure vault.
- Prefer **key-based authentication** for better security.

---

## Troubleshooting
- **Authentication failed**: Check credentials or key file permissions.
- **Permission denied**: Ensure the remote user has write access to `REMOTE_FOLDER`.
- **Connection timeout**: Verify network connectivity and firewall rules.

---

## Credits
- Built by **Piero Olivas**.
