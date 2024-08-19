# loads envorinment variables from .env file

import os

from dotenv import load_dotenv

load_dotenv()

API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
BOTNAME = os.getenv("BOTNAME")

assert API_ID, "API_ID is not set"
assert API_HASH, "API_HASH is not set"
assert BOTNAME, "BOTNAME is not set"
