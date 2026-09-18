# E2EE Ephemeral CLI Chat

A multi-threaded CLI chat client in Python featuring End-to-End Encryption (E2EE) via X25519 and AES-256-GCM, self-destructing messages, and a session panic switch with RAM key zeroization.

---

## Features

* **Ephemeral Key Exchange:** Key agreement using X25519 ECDH and HKDF (SHA-256). Shared secrets are derived locally and never transmitted.
* **Authenticated Encryption:** Payload encryption using AES-256-GCM with a unique 12-byte initialization vector (`os.urandom(12)`) per message.
* **Self-Destructing Messages:** Asynchronous background timers (`threading.Timer`) and ANSI escape codes (`\033[2K\033[1A`) clear rendered messages from the terminal after 5 seconds.
* **Panic Switch:** Emergency shutdown via `/panic` or `Ctrl+C` clears the console screen and overwrites key material in RAM memory (`b'\x00' * 32`).
* **Non-Blocking Threading:** Concurrent socket listening and user input loops.

---

## Architecture

```text
+-----------------------------------------------------------------------+
|                             KEY HANDSHAKE                             |
|                                                                       |
|   Client A                                                Client B    |
|  [ Private Key ]                                         [ Private Key ]
|        |                                                       |      |
|  (Generate PubKey)                                     (Generate PubKey)|
|        |---- Transmit Public Key (32 bytes) ------------------>|      |
|        |<--- Transmit Public Key (32 bytes) -------------------|      |
|        |                                                       |      |
|  [ X25519 ECDH ]                                       [ X25519 ECDH ]|
|        |                                                       |      |
|  (Raw Secret)                                           (Raw Secret)  |
|        |                                                       |      |
|  [ HKDF SHA-256 ]                                      [ HKDF SHA-256 ]|
|        |                                                       |      |
|  => 32-Byte Shared Key                                 => 32-Byte Shared Key
+-----------------------------------------------------------------------+
```
1. **Handshake:** Both peers generate ephemeral X25519 keypairs and exchange 32-byte public keys over the TCP socket.
2. **Key Derivation:** Both parties independently derive a matching symmetric 256-bit AES key using HKDF (SHA-256).
3. **Payload Construction:** Outgoing traffic is encrypted with AES-256-GCM using a random 12-byte IV.

```text
+-----------------------+---------------------------------------+
|   IV (First 12 Bytes)  |  Ciphertext + Auth Tag (Remaining)   |
+-----------------------+---------------------------------------+
```
4. Decryption: The receiving client extracts data[:12] as the IV and decrypts data[12:].
---

## Requirements

* Python 3.8+
* `cryptography` package

---

## Usage

### 1. Installation

```bash
git clone [https://github.com/kashczynski/E2EE-Ephemeral-CLI-Chat.git](https://github.com/kashczynski/E2EE-Ephemeral-CLI-Chat.git)
cd E2EE-Ephemeral-CLI-Chat
pip install cryptography
```
2. Run Client:
   ```bash
   python client.py
   ```

3. Commands
Send Message: Type message and press Enter.

Exit: Type exit to disconnect.

Emergency Panic: Type /panic or press Ctrl+C to purge screen output and zero out key material.   

4. Security Details   
Perfect Forward Secrecy: Session keys reside strictly in volatile memory and are destroyed upon process termination.   

Replay Protection: Unique 12-byte IVs per transmission prevent identical ciphertext outputs.   

Memory Scrubbing: The panic handler zero-fills the 32-byte shared_aes_key variable prior to exitin

Memory Scrubbing: The panic handler zero-fills the 32-byte shared_aes_key variable prior to exiting.
   
