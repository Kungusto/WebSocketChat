import sys
from pathlib import Path

# добавление src в поле видимости
sys.path.append(str(Path(__file__).parent.parent))

import logging
import asyncio
from src.services.socket_conn import SocketManager
from src.exceptions import NoConnectionsNow

async def handle_client(server_socket, connection):
    server_socket.handling_connections.append(connection)
    try:
        while True:
            message = await server_socket.get_message(connection)
            if message:
                print(f"Michael: {message}")
                await server_socket.send_all(f"John: {message}".encode("utf-8"))
    except ConnectionResetError:
        print("Клиент отключился")
    finally:
        server_socket.active_connections.remove(connection)
        server_socket.handling_connections.remove(connection)

async def main():
    logging.basicConfig(level=logging.DEBUG, 
                        format='%(asctime)s - %(levelname)s - %(message)s')
    logging.info("Запуск сервера")
    server_socket = SocketManager()
    server_socket.bind(('127.0.0.1', 8000))
    server_socket.listen()
    try:
        while True:
            print("В ожидании соединения")
            try:
                await server_socket.accept()
                print(f"Соединение установлено: {server_socket.connections[-1]}")
            except NoConnectionsNow:
                logging.info("Соединений не обнаружено")
            tasks = [
                asyncio.create_task(handle_client(server_socket, conn))
                for conn in server_socket.active_connections
                if conn not in server_socket.handling_connections
            ]
            if tasks:
                await asyncio.gather(*tasks)
    except KeyboardInterrupt:
        print("Выход из программы")
    finally:
        server_socket.close()

asyncio.run(main())