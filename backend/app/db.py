"""
File: supabase_client.py
Project: app
File Created: Thursday, 20th November 2025 3:47:15 PM
Author: baaba-midnight
Email: baaba.amosah@gmail.com
Version: 1.0
Brief: A module to connect to a Supabase PostgreSQL database using environment variables.
-----
Last Modified: Saturday, 22nd November 2025 4:03:09 PM
Modified By: baaba-midnight
-----
Copyright ©2025 baaba-midnight
"""
import os
import psycopg2
from supabase import create_client, Client
from dotenv import load_dotenv

# load environment variables from .env file
load_dotenv()

# Supabase Client -  export this for most operations
supabase_url: str = os.environ.get("supabase_url")
supabase_key: str = os.environ.get("supabase_key")
supabase: Client = create_client(supabase_url, supabase_key)

# fetch variables: using spooler for IPv4
USER = os.getenv("user")
PASSWORD = os.getenv("password")
HOST = os.getenv("host")
PORT = os.getenv("port")
DBNAME = os.getenv("dbname")

_pg_connection = None

def get_pg_connection():
    """Get PostgresSQL connection"""
    global _pg_connection

    if _pg_connection is None or _pg_connection.closed:
        _pg_connection = psycopg2.connect(
            user=USER,
            password=PASSWORD,
            host=HOST,
            port=PORT,
            dbname=DBNAME
        )
    return _pg_connection

def close_pg_connection():
    """Close PostgreSQL connection"""
    global _pg_connection
    if _pg_connection and not _pg_connection.closed:
        _pg_connection.close()