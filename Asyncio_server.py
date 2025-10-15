import socket
import asyncio
import logging

# ========== INITIAL CONFIG ==========

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s"
)

HOST = "127.0.0.1"
PORT = 8888

clients = {}
lock = asyncio.Lock()

# ========== TRASMISSION FUNCTIONS ==========

# Funzione per inviare il messaggio a tutti i client tranne a quello da cui arriva
async def broadcast(message, exclude_writer=None):
    async with lock:
        for writer in clients:
            if writer != exclude_writer:
                try:
                    writer.write((message + "\n").encode())
                    await writer.drain()
                except:
                    writer.close()

# Funzione per ricezione dei messaggi con controllo del \n
async def ricevi_messaggio(reader):
    buffer = ""
    while True:
        try:
            data = await reader.read(1024)
            if not data:
                return None
            buffer += data.decode()
            if "\n" in buffer:
                message, buffer = buffer.split("\n", 1)
                return message.strip()
        except:
            return None

# Funzione per gestione del client finché è connesso
async def gestisci_client(reader, writer):
    writer.write("Inserisci il tuo nome:\n".encode())
    await writer.drain()

    name = await ricevi_messaggio(reader)
    if not name:
        writer.close()
        return

    async with lock:
        clients[writer] = name
    addr = writer.get_extra_info("peername")
    logging.info(f"{name} connesso da {addr}")
    await broadcast(f"{name} è entrato nella chat.", exclude_writer=writer)

    try:
        while True:
            message = await ricevi_messaggio(reader)
            if message is None:
                break
            if message == "/exit":
                await broadcast(f"{name} ha lasciato la chat.", exclude_writer=writer)
                break
            await broadcast(f"{name}: {message}", exclude_writer=writer)
    except:
        pass
    finally:
        async with lock:
            logging.info(f"{name} disconnesso.")
            await broadcast(f"{name} ha abbandonato la chat.", exclude_writer=writer)
            clients.pop(writer, None)
        writer.close()

# ========== MAIN LOOP ==========

async def main():
    server = await asyncio.start_server(gestisci_client, HOST, PORT)
    addr = server.sockets[0].getsockname()
    logging.info(f"Server in ascolto su {addr[0]}:{addr[1]}")

    async with server:
        try:
            await server.serve_forever()
        except KeyboardInterrupt:
            logging.info("\nServer interrotto manualmente.")

if __name__ == "__main__":
    asyncio.run(main())
