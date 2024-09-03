import uvicorn
from web import app 
from web.functions import *

if __name__ == "__main__":
    try:
        ServerManager.cls()
        Application.setup()
        ServerManager.server_log(text="Успешный запуск сервера.",type=1, e=None)
        uvicorn.run("web:app", port=5000, host="0.0.0.0")
    except KeyboardInterrupt:
        ServerManager.server_log(text="Отключение сервера.",type=1, e=None)
        ServerManager.shutdown_server()
