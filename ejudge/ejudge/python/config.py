"""Shared connection helper. Reads settings from .env (see .env.example)."""
import os

import oracledb
from dotenv import load_dotenv

load_dotenv()

# Return CLOB columns as plain Python str
oracledb.defaults.fetch_lobs = False


def get_connection() -> oracledb.Connection:
    kwargs = dict(
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        dsn=os.environ["DB_DSN"],
    )
    # Autonomous Database (wallet) support
    if os.getenv("DB_WALLET_DIR"):
        kwargs.update(
            config_dir=os.environ["DB_WALLET_DIR"],
            wallet_location=os.environ["DB_WALLET_DIR"],
            wallet_password=os.getenv("DB_WALLET_PASSWORD"),
        )
    return oracledb.connect(**kwargs)
