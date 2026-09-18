import socket
import threading
import sys
import os
import time

from cryptography.hazmat.primitives.asymmetric import x25519
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


HOST = '127.0.0.1'
PORT = 65432

def receive_messages(client_socket, shared_aes_key):
    aesgcm=AESGCM(shared_aes_key)

    while True:
        try:
            raw_data=client_socket.recv(4096)
            if not raw_data:
                print("\n[DISCONNECTED] server closed the connection")
                print("\n{message}\n>", end='')
            iv=raw_data[:12]
            ciphertext=raw_data[12:]
            decrypted_bytes=aesgcm.decrypt(iv, ciphertext, associated_data=None)
            message=decrypted_bytes.decode('utf-8')

            print(f"\n[Peer]: {message}\n> ", end='', flush=True)
        except ConnectionResetError:
            print("\n[ERROR] Connection to the server lost")
            break
        except Exception:
            break


def start_client():
    
    client_socket=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect((HOST, PORT))
        print(f"[CONNECTED] connected to the broadcast server at {HOST}:{PORT}")
        local_private_key = x25519.X25519PrivateKey.generate()
        local_public_key= local_private_key.public_key()
        client_socket.send(local_public_key.public_bytes_raw())


        peer_bytes = client_socket.recv(32)
        peer_public_key = x25519.X25519PublicKey.from_public_bytes(peer_bytes)
        raw_shared_secret = local_private_key.exchange(peer_public_key)
        shared_aes_key=HKDF(
            algorithm=hashes.SHA256(32),
            salt=None,
            info=b'handshake data',


        ).derive(raw_shared_secret)
        
        print("[SECURE] Shared key established. End-to-end encryption active.")
        print("Type your messages below. Type 'exit' to disconnect.\n")
        receive_thread = threading.Thread(target=receive_messages, args=(client_socket, shared_aes_key))
        receive_thread.daemon = True
        receive_thread.start()
        aesgcm=AESGCM(shared_aes_key)
        while True:
            
            msg=input("> ")
            if msg.lower()=='exit':
                break
            if msg.strip():
                iv=os.urandom(12)
                ciphertext=aesgcm.encrypt(iv, msg.encode('utf-8'), associated_data=None)
                client_socket.send(iv+ciphertext)
    except ConnectionRefusedError:
        print(f"[ERROR] Unable to connect to the server at {HOST}:{PORT}. Is the server running?")
    finally:
        client_socket.close()
        print("[DISCONNECTED] client disconnected from the server")


if __name__ == "__main__":
    start_client()
