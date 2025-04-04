import socket
import asyncio
from src.exceptions import NoConnectionsNow

class SocketManager :
    connections = []
    handling_connections = []
    
    def __init__(self):
        self.socket = self.get_conn_to_socket()
        self.clients_address = []
        self.active_connections = []
        self.current_connection = None
        self.socket.setblocking(False)

    @staticmethod
    def get_conn_to_socket() :
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return server_socket

    @property
    def event_loop(self) :
        return asyncio.get_event_loop()

    def set_current_connection(self, connection) : 
        self.connection = connection

    def bind(self, address) :
        self.socket.bind(address)    

    async def accept(self) :
        try: 
            connection, client_address = await asyncio.wait_for(
                self.event_loop.sock_accept(self.socket), timeout=0.1
                ) 
            self.connection = connection
            self.active_connections.append(connection)
            self.connections.append(client_address)
            self.clients_address = client_address
        except TimeoutError : 
            raise NoConnectionsNow from TimeoutError
            
        

    def listen(self) :
        self.socket.listen()

    async def get_message(self, connection) : 
        buffer = b''
        start_message = "Michael(You): ".encode("utf-8")
        await self.event_loop.sock_sendall(connection, b"\r" + start_message)
        while True :
            data = await self.event_loop.sock_recv(connection, 1024)
            if data != b"\r\n" :
                if data == b"\x03" : 
                    break
                if data == b"\x08" :
                    buffer = buffer[:-1]
                    await self.event_loop.sock_sendall(connection, b"\r")
                    await self.event_loop.sock_sendall(connection, b" "*len(start_message) + b" "*(len(buffer)+3))
                else :
                    buffer += data
                await self.event_loop.sock_sendall(connection, b"\r")
                await self.event_loop.sock_sendall(connection, start_message + buffer)
            else :
                return buffer.decode("utf-8")

    async def send_message(self, text) :
        await self.event_loop.sock_sendall(self.connection, text)

    async def send_all(self, text) :
        await asyncio.gather(
            *(self.event_loop.sock_sendall(connect, text) for connect in self.active_connections)
        )
    
    async def close(self) :
        self.socket.close()
        