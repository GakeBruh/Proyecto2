import os
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.server_api import ServerApi

load_dotenv()

DB = os.getenv("MONGO_DB_NAME")
URI = os.getenv("URI")

def get_collection( col ):
    client = MongoClient(  
        URI
        , server_api = ServerApi("1")
        , tls = True
        , tlsAllowInvalidCertificates = True
    )
    client.admin.command("ping")
    return client[DB][col]