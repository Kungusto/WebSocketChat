import socket
import asyncio
import logging
from src.exceptions import NoConnectionsNow

class SocketManager:
    connections = []
    handling_connections = []
    
    def __init__(self):
        self.socket = self.get_conn_to_socket()
        self.clients_address = []
        self.active_connections = []
        self.current_connection = None
        self.socket.setblocking(False)

    @staticmethod
    def get_conn_to_socket():
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return server_socket

    @property
    def event_loop(self):
        return asyncio.get_event_loop()

    def set_current_connection(self, connection):
        self.connection = connection

    def bind(self, address):
        self.socket.bind(address)    

    async def accept(self):
        try:
            connection, client_address = await asyncio.wait_for(
                self.event_loop.sock_accept(self.socket), timeout=0.1
            )
            self.active_connections.append(connection)
            self.connections.append(client_address)
            logging.info(f"Новое соединение: {client_address}")
        except asyncio.TimeoutError:
            raise NoConnectionsNow

    def listen(self):
        self.socket.listen()

    async def get_message(self, connection):
        buffer = b''
        start_message = "Michael(You): ".encode("utf-8")
        await self.event_loop.sock_sendall(connection, b"\r" + start_message)
        while True:
            try:
                data = await self.event_loop.sock_recv(connection, 1024)
                logging.debug(f"Получены данные: {data}")
                if data == b"\x03":  # Ctrl+C
                    break
                elif data == b"\x08":  # Backspace
                    buffer = buffer[:-1]
                else:
                    buffer += data
                await self.event_loop.sock_sendall(connection, b"\r" + start_message + buffer)
            except ConnectionResetError:
                logging.warning("Соединение с клиентом потеряно")
                self.active_connections.remove(connection)
                break
        return buffer.decode("utf-8")

    async def send_message(self, text):
        if self.connection:
            await self.event_loop.sock_sendall(self.connection, text)

    async def send_all(self, text):
        for connect in self.active_connections:
            try:
                await self.event_loop.sock_sendall(connect, text)
            except ConnectionResetError:
                logging.warning("Соединение с клиентом потеряно")
                self.active_connections.remove(connect)

    def close(self):
        for connection in self.active_connections:
            connection.close()
        self.socket.close()
        logging.info("Сервер закрыт")
