import socket
import threading
import logging

# ========== INITIAL CONFIG ==========

# Logging configuration
logging.basicConfig(
    level=logging.INFO, 
    format="%(message)s"
)

SERVER_HOST = "127.0.0.1"
SERVER_PORT = 8888

# ========== COMUNICATION FUNCIONS ==========

def ricevi_messaggi(socket):
    buffer = ""
    while True:
        try:
            data = socket.recv(1024)
            if not data:
                logging.info("Connessione chiusa dal server.")
                break
            buffer += data.decode()
            while "\n" in buffer:
                message, buffer = buffer.split("\n", 1)
                if message.strip():
                    logging.info(message.strip())
        except:
            break
        
# ========== MAIN LOOP ==========

def main():
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((SERVER_HOST, SERVER_PORT))
    except Exception as e:
        logging.info(f"Errore di connessione al server: {e}")
        return

    try:
        # Ricevi la richiesta del nome
        buffer = ""
        while True:
            data = client_socket.recv(1024)
            if not data:
                logging.info("Connessione chiusa dal server.")
                return
            buffer += data.decode()
            if "\n" in buffer:
                msg, buffer = buffer.split("\n", 1)
                logging.info(msg.strip())
                break

        name = input("> ")
        client_socket.sendall(name.encode() + b"\n")

        threading.Thread(target=ricevi_messaggi, args=(client_socket,), daemon=True).start()

        while True:
            message = input("> ")
            client_socket.sendall(message.encode() + b"\n")
            if message.strip() == "/exit":
                logging.info("Disconnessione in corso...")
                break

    except Exception as e:
        logging.info(f"Errore durante la comunicazione: {e}")
    finally:
        client_socket.close()

if __name__ == "__main__":
    main()