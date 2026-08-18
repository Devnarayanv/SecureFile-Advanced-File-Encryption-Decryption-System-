# SecureFile – Class Presentation & Project Defense Guide

This document is a structured presentation guide to help you explain the **SecureFile** application in class. It highlights the architecture, cryptography specs, core Operating System concepts, and includes a live demo script and typical Q&A defense questions.

---

## 1. Project Overview & Pitch
* **The Goal**: Build a fully functional, highly secure desktop application for file protection that directly illustrates practical OS resource allocation theories.
* **The Problem It Solves**: Basic file utilities freeze windows during heavy disk I/O, store passwords insecurely, or use mock encryption (like XOR). SecureFile solves these using **non-blocking worker threads**, **PBKDF2-HMAC-SHA256 password hashing**, and **AES-256 GCM chunked streaming**.

---

## 2. Core OS Concepts Demonstrated
Use this section to show how the project satisfies the Operating Systems curriculum:

### A. Process & Thread Management
* **The Challenge**: GUI operations run on a single main event loop thread. Heavy cryptographic operations block this thread, causing the window to freeze.
* **The OS Solution**: SecureFile creates a background worker thread (`threading.Thread`) to execute the encryption/decryption pipeline.
* **Telemetries Shown**: The GUI queries process attributes in real time, displaying:
  * Current process ID (PID).
  * Active Thread Count (CPU core distribution).
  * Worker thread identities.

### B. File System Management
* **Data Metadata Persistence**: On encryption, the program reads the file size and access permissions (`os.stat`). It packages them *inside* the encrypted stream. On decryption, it restores the original file permission bitmasks via `os.chmod`.
* **Safe Cleanups**: On validation failure, the application calls the OS to immediately clear writing fragments to avoid leaving corrupted file garbage on the drive.

### C. Storage Management
* **Pre-flight Capacity Checks**: Before beginning heavy disk writes, the application calculates sectors size limits via `shutil.disk_usage` on the destination drive, preventing disk exhaustion errors.
* **File Amplification**: Displays original file sizes vs. actual encrypted container sizes.

### D. Resource Allocation Diagnostics
* **Handle Leak Prevention**: Monitors active OS file descriptors (`proc.num_fds`) on Unix or kernel handles (`proc.num_handles`) on Windows to detect leaks.
* **Memory Constraints**: Tracks Resident Set Size (RSS) memory consumption in real time.

---

## 3. Cryptographic Design (AES-256 GCM Chunked)
Explain why this design is cryptographically secure:

1. **PBKDF2-HMAC-SHA256 (100,000 Iterations)**: Computes a secure 256-bit AES key from a user password using a unique 16-byte random salt. This defends against rainbow table lookup attacks.
2. **Authenticated Encryption (GCM)**: Unlike basic AES modes (like CBC), GCM appends an authentication tag. This ensures **ciphertext integrity**; if an attacker modifies even 1 bit of the encrypted file, decryption fails instantly before writing data to disk.
3. **Nonce Scheduling**: Generates a 12-byte base nonce. Each 1MB block is encrypted with an incrementing nonce: `Base Nonce + Chunk Index`, preventing nonce-reuse key exposure.
4. **Encrypted Headers**: Filenames and extensions are encrypted inside the container to prevent metadata leakage.

---

## 4. Live Demo Walkthrough Script

Follow these steps during your in-class demonstration:

| Step | Action | What to Explain |
| :--- | :--- | :--- |
| **1. The Lockout** | Enter `admin` and a wrong password 3 times. | "Notice that after 3 failed attempts, the OS lockout mechanism triggers a 30s timer. This lockout state is stored in SQLite, so restarting the app will not reset the cooldown." |
| **2. Login** | Log in with `admin` / `Admin@123`. | "We are authenticated. The main interface loads, and the background system monitor starts querying telemetry." |
| **3. Live Monitor** | Point to the bottom-right System Monitor. | "This dashboard shows live stats. Notice CPU, RAM, and active OS handles. This is polled dynamically using `psutil`." |
| **4. Encryption** | Go to **Encrypt File**, browse a file (~2MB+), type password, and encrypt. | "Watch the progress bar. Notice the window is fully responsive; you can move it or switch tabs because the work is running on a separate thread. Look at the thread ID showing the active worker." |
| **5. Audit Check** | Go to **Activity Logs**. | "Every action, successful or failed, is logged in SQLite with timestamp and duration metrics. We can export this database history to a CSV spreadsheet." |
| **6. Corruption Test** | Open the encrypted `.secure` file in a text editor, insert random characters, save, then try to decrypt. | "AES-GCM checks authenticity. Because the file was modified, the decryption engine raises an integrity error, stops, and deletes the corrupted output file immediately." |

---

## 5. Potential Defense Questions (Q&A)

* **Q: Why did you use Threads instead of Multiprocessing in Python?**
  * *A*: Threads share the memory space of the main process, allowing the background worker to easily update progress variables. Since file encryption is heavily bound by Disk I/O, Python's GIL (Global Interpreter Lock) is released during read/write calls, making threads highly efficient without process fork overhead.
* **Q: How does the system verify the decryption password without storing it?**
  * *A*: The system derives the AES-256 key from the password. During decryption of the first chunk, AES-GCM attempts to decrypt the ciphertext. If the password is wrong, the GCM tag authentication check fails, throwing an `InvalidTag` exception.
* **Q: Why is the salt stored in plaintext inside the `.secure` file?**
  * *A*: A salt does not need to be secret; its purpose is to ensure that two identical passwords derive different keys. The decrypter reads this salt to re-run the PBKDF2 function and derive the same key.
