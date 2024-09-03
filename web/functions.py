import json
import os
import signal
import datetime
import platform
import subprocess
import re
from colorama import init, Fore
import socket
import requests
import hashlib
import secrets
import pymongo

init()

class ConfigManager:
    @staticmethod
    def open_config(config_name="config.json"):
        with open(config_name, 'r') as file:
            data = json.load(file)
        return data

    @staticmethod
    def write_config(config, config_name="config.json"):
        with open(config_name, 'w') as file:
            json.dump(config, file, indent=4)

class ServerManager:
    @staticmethod
    def shutdown_server():
        os.kill(os.getpid(), signal.SIGINT)

    @staticmethod
    def timestamp():
        return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    @staticmethod
    def create_hash(variable):
        variable = str(variable)
        variable += "$jhNmfH%2BMdGkfF@aHLe7LyuAu!rxU$ZS3oxPjwEwCGRAfPceTdjkDMhEyy8S#D28B9EeP4TqvzzW#3qLiuUgy9gc8qK2zk923P@%&Z9QK7vopzK4gY3f*HN%8pp"
        variable_bytes = variable.encode("utf-8")
        hashed_variable = hashlib.sha256(variable_bytes).hexdigest()
        return str(hashed_variable)

    @staticmethod
    def server_log(text: str, type: int = 1, e: Exception = None):
        from web import database
        if type == 1:
            print(Fore.GREEN + "INFO" + Fore.RESET + ":" + f"     {text}")
        else:
            print(Fore.RED + "Error" + Fore.RESET + ":" + f"     {text}" + str(e))
        database["server_logs"].insert_one({
            "text": text,
            "timestamp": ServerManager.timestamp(),
        })

    @staticmethod
    def cls():
        if os.name == "nt":
            os.system("cls")
        else:
            os.system("clear")

class NetworkManager:
    @staticmethod
    def ping(host, type=1):
        try:
            system = platform.system()
            if system == "Windows":
                ping_command = ["ping", "-n", "5", "-w", "1000", host]
                time_pattern = r'время[=<](\d+)'
            else:
                ping_command = ["ping", "-c", "5", "-W", "1", host]
                time_pattern = r'time[=<](\d+\.\d+)'

            output = subprocess.check_output(
                ping_command,
                stderr=subprocess.STDOUT,
                universal_newlines=True
            )

            if type == 1:
                return True
            elif type == 2:
                match = re.search(time_pattern, output)
                if match:
                    return float(match.group(1)) if '.' in match.group(1) else int(match.group(1))
                return None
        except subprocess.CalledProcessError as e:
            print(f"CalledProcessError: {e.output}")
            return False if type == 1 else None
        except FileNotFoundError as e:
            print(f"FileNotFoundError: {e}")
            return False if type == 1 else None
        except ValueError as e:
            print(f"ValueError: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error: {e}")
            return False if type == 1 else None

class UserManager:
    @staticmethod
    def root_user():
        from web import database
        data = ConfigManager.open_config()
        root_nickname = data["setup"]["root_user"]["login"]
        root_password = data["setup"]["root_user"]["password"]
        root_password = ServerManager.create_hash(root_password)

        token = secrets.token_urlsafe(256)

        user = database["users"].find_one({"username": f"{root_nickname}"})
        if user:
            try:
                database["users"].update_one(
                    {"username": root_nickname},
                    {"$set": {"password": root_password, "session.token": token}}
                )
                ServerManager.server_log(text="Удачная попытка обновления суперпользователя.", type=1)
            except pymongo.errors.OperationFailure as e:
                ServerManager.server_log(text="Неудачная попытка обновления суперпользователя.", type=2, e=e)
        else:
            try:
                database["users"].insert_one({
                    "username": root_nickname,
                    "password": root_password,
                    "session": {
                        "token": token
                    },
                    "permissions": {
                        "administrator": True
                    }
                })
                ServerManager.server_log(text="Удачная попытка создания суперпользователя.", type=1)
            except pymongo.errors.OperationFailure as e:
                ServerManager.server_log(text="Неудачная попытка создания суперпользователя.", type=2, e=e)
    
    @staticmethod
    def check_auth(Response, request):
        auth = request.cookies.get('auth')
        if auth == True:
            from web import database
            auth_token = request.cookies.get('auth_token')
            user = database["users"].find_one({"session":{"token": f"{auth_token}"}})
            if user:
                return True
            else:
                return False
        else:
            return False

class Application:
    @staticmethod
    def setup():
        try:
            ServerManager.server_log("Попытка конфигураций сервера.", type=1, e=None)
            UserManager.root_user()
            google_dns = NetworkManager.ping(host="8.8.8.8")
            cloudflare_dns = NetworkManager.ping(host="1.1.1.1")
            ping_list = [google_dns, cloudflare_dns]

            config = ConfigManager.open_config()

            if True in ping_list:
                internet = True
                external_ip = requests.get('https://httpbin.org/ip').json()['origin']
                print(Fore.GREEN + "INFO" + Fore.RESET + ":" + "     Нормальная работа интернета.")
            else:
                internet = False
                external_ip = False
                print(Fore.RED + "INFO" + Fore.RESET + ":" + "     Отсутствие интернет соединения.")

            local_ip = socket.gethostbyname(socket.gethostname())
            config['system']['external_ip'] = external_ip
            config['system']['local_ip'] = local_ip
            config['system']['os'] = os.name
            config['system']['internet_status'] = internet
            ConfigManager.write_config(config)
            ServerManager.server_log("Успешная конфигурация сервера.", type=1, e=None)
        except Exception as e:
            ServerManager.server_log(text="Неудачная конфигурация сервера.", type=2, e=e)
            ServerManager.shutdown_server()

if __name__ == "__main__":
    pass
