from dotenv import load_dotenv
import os

load_dotenv()


MYSQL_USER = os.getenv("MYSQL_USER", "root")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
MYSQL_DB = os.getenv("MYSQL_DB", "cbfmanager")
MYSQL_PORT = int(os.getenv("MYSQL_PORT", 3306))

host = MYSQL_HOST
port = MYSQL_PORT

if host and ":" in host:
    host, host_port = host.rsplit(":", 1)
    if not port:
        port = host_port

HOST_WITH_PORT = f"{host}:{port}" if port else host