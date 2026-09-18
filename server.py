import socket
import threading

HOST='127.0.0.1'
PORT=65432

clients=[]

def broadcast_message(message, sender_socket):
    for client in clients:
        if client !=sender_socket:
            try:
                client.send(message.encode('utf-8'))          
            except Exception as e:
                print(f"Error sending message to client: {e}")
                clients.remove(client)
                client.close()




def handle_client(client_socket, client_address):
    print(f"[NEW CONNECTION] {client_address} connected")
    clients.append(client_socket)
    try:
        while True:
            message=client_socket.recv(4096).decode('utf-8')
            if not message:
                break
            print(f'[{client_address}] {message}')
    except ConnectionResetError:
        pass
    finally:
        if client_socket in clients:
            clients.remove(client_socket)
        client_socket.close()
        print(f"[DISCONNECTED] {client_address}disconnected")




def start_server():
    server_socket=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen()
    print(f"Server listening on {HOST}:{PORT}")
    try:
        while True:
            client_socket, client_address=server_socket.accept()
            thread=threading.Thread(target=handle_client, args=(client_socket, client_address))
            thread.daemon=True
            thread.start()

            print(f"[ACTIVE_CONNECTIONS] {len(clients)}")
    except KeyboardInterrupt:
        print("Server not working... shutting down")
    finally:
        server_socket.close()



if __name__=="__main__":
    start_server()
