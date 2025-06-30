from dotenv import load_dotenv
import os

load_dotenv()

MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_DB = os.getenv("MYSQL_DB")
MYSQL_PORT = os.getenv("MYSQL_PORT")

host = MYSQL_HOST
port = MYSQL_PORT

# Logic to correctly parse host and port, making the configuration more robust.
# This handles cases where the port might be included in the MYSQL_HOST variable.
if host and ":" in host:
    # Split host and port from the right, which is safer
    host, host_port = host.rsplit(":", 1)
    # The explicit MYSQL_PORT variable takes precedence.
    # If it's not set, we use the one found in MYSQL_HOST.
    if not port:
        port = host_port

# Reconstruct the final host string for the URI
HOST_WITH_PORT = f"{host}:{port}" if port else host

MYSQL_URI = (
    f"mysql+pymysql://"
    f"{MYSQL_USER}:{MYSQL_PASSWORD}@{HOST_WITH_PORT}/{MYSQL_DB}"
)
