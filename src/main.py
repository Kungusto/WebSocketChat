import sys
from pathlib import Path

# добавление src в поле видимости
sys.path.append(str(Path(__file__).parent.parent))

import logging
import asyncio
import threading
from src.services.socket_conn import SocketManager
from src.exceptions import NoConnectionsNow

async def handle_client(server_socket, connection):
    server_socket.handling_connections.append(connection)
    while True:
        try:
            message = await server_socket.get_message(connection)
            print(f"Michael: {message}")
            await server_socket.send_all(
                f"John: {message}".encode("utf-8") if message else ...
            )
        except ConnectionResetError:
            print("Клиент отключился")
            server_socket.active_connections.remove(connection)
            break

async def main() : 
    server_socket = SocketManager()
    server_socket.bind(('127.0.0.1', 8000))
    server_socket.listen()
    server_socket.socket.setblocking(False)
    loop = asyncio.get_event_loop()
    while True :
        try :
            print("В ожидании соединения")
            try :
                await server_socket.accept()   
                print(f"Соединение установлено: {server_socket.active_connections[-1]}")
            except NoConnectionsNow:
                print("Соединений не обнаружено")
            tasks = [
                asyncio.create_task(handle_client(server_socket, conn)) 
            for conn in server_socket.active_connections
            if conn not in server_socket.handling_connections
            ]
            print(tasks)
            await asyncio.gather(*tasks)
        except BlockingIOError :
            print("Соединений не обнаружено")
        except KeyboardInterrupt :
            print("Выход из программы")
            break
    server_socket.close()

asyncio.run(main())