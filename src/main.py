import sys
from pathlib import Path

# добавление src в поле видимости
sys.path.append(str(Path(__file__).parent.parent))

import logging
from src.services.socket_conn import SocketManager
import asyncio
import threading

async def main() : 
    server_socket = SocketManager()
    server_socket.bind(('127.0.0.1', 8000))
    server_socket.listen()
    server_socket.socket.setblocking(False)

    try :
        while True :
            await server_socket.accept()        
            for index, (conn, address, name) in enumerate(server_socket.active_connections) :
                try :
                    message = conn.recv(1024)
                    try :
                        message.decode()
                    except UnicodeDecodeError :
                        del server_socket.active_connections[index]
                        for ___conn, ___address, ___name in server_socket.active_connections :
                                ___conn.send(b"\r" + name
                                            .strip().encode("utf-8") + b" left the chat\n" + __name.strip().encode("utf-8") + b"(you): ")
                        conn.close()
                        continue
                    conn.send(name.encode("utf-8") + b"(you): ")
                    print(f"Получено сообщение{name} : {message.decode().strip()}")
                    for _conn, _, _name in server_socket.active_connections :
                        if _conn != conn : 
                            _conn.send(b"\r" + (" "*20).encode("utf-8") + b"\r" + f"{name}: ".encode("utf-8") + message + _name.strip().encode("utf-8") + b"(you): ")

                except BlockingIOError : 
                    ...
            for conn, address in server_socket.authorization_connections :
                try :
                    name = conn.recv(1024)
                    if name :
                        server_socket.set_active_connection((conn, address, name.decode().strip()))
                    conn.send(b"Your authorized as: " + name)
                    server_socket.authorization_connections.remove((conn, address))
                    for __conn, __address, __name in server_socket.active_connections :
                        if __conn != conn :
                            __conn.send(b"\r" + name.decode().strip().encode("utf-8") + b" joined the chat\n" + __name.strip().encode("utf-8") + b"(you): ")
                    conn.send(("-"*100).encode("utf-8") + b"\n")
                    conn.send(name.decode().strip().encode("utf-8") + b"(you): ")
                except BlockingIOError : 
                    ...
    except KeyboardInterrupt :
        print("Закрытие сокета")

asyncio.run(main())