import socket
import threading
import logging

# ========== INITIAL CONFIG ==========

# Logging configuration
logging.basicConfig(
    level=logging.INFO, 
    format="%(message)s"
)

HOST = "127.0.0.1"
PORT = 8888

# Server socket creation
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((HOST, PORT))
server.listen()

clients = {}
lock = threading.Lock()

logging.info(f"Server avviato su {HOST}:{PORT}")

# ========== TRASMISSION FUNCIONS ==========

# Funzione per inviare il messaggio a tutti i client tranne a quello da cui arriva
def broadcast(message, exclude_socket=None):
    with lock:
        for client_socket in clients:
            if client_socket != exclude_socket:
                try:
                    client_socket.sendall(message.encode() + b"\n")
                except:
                    client_socket.close()

# Funzione per ricezione dei messaggi con controllo del /n
def ricevi_messaggio(socket):
    buffer = ""
    while True:
        try:
            data = socket.recv(1024).decode()
            if not data:
                return None
            buffer += data
            if "\n" in buffer:
                message, buffer = buffer.split("\n", 1)
                return message.strip()
        except:
            return None

# Funzione per gestione del client finché è connesso
def gestisci_client(client_socket, client_address):
    try:
        client_socket.sendall("Inserisci il tuo nome:\n".encode())
        name = ricevi_messaggio(client_socket)

        with lock:
            clients[client_socket] = name
        logging.info(f"{name} connesso da {client_address}")
        broadcast(f"{name} è entrato nella chat.", exclude_socket=client_socket)

        while True:
            message = ricevi_messaggio(client_socket)
            if message is None:
                break

            if message == "/exit":
                broadcast(f"{name} ha lasciato la chat.", exclude_socket=client_socket)
                break

            broadcast(f"{name}: {message}", exclude_socket=client_socket)
    except:
        pass
    finally:
        with lock:
            name = clients.get(client_socket, "Utente sconosciuto")
            logging.info(f"{name} disconnesso.")
            broadcast(f"{name} ha abbandonato la chat.", exclude_socket=client_socket)
            clients.pop(client_socket, None)
        client_socket.close()

# ========== MAIN LOOP ==========

def main():
    while True:
        try:
            client_socket, client_address = server.accept()
            thread = threading.Thread(target=gestisci_client, args=(client_socket, client_address))
            thread.daemon = True
            thread.start()
        except KeyboardInterrupt:
            logging.info("\nServer interrotto manualmente.")
            break

    server.close()

if __name__=="__main__":
    main()