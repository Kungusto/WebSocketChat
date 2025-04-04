class SocketBaseException(Exception):
    detail = "Неожиданная ошибка"

    def __init__(self, *args, **kwargs):
        super().__init__(self.detail, *args, **kwargs)
        
class NoConnectionsNow(SocketBaseException):
    detail = "Нет доступных соединений. Проверьте, что клиент подключен и повторите попытку."