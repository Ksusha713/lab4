import bcrypt
from motor.motor_asyncio import AsyncIOMotorClient

MONGO_URL = "mongodb://127.0.0.1:27017"
client = AsyncIOMotorClient(MONGO_URL)
db = client.ip
users_collection = db.get_collection("users")
data_collection = db.get_collection("data")

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    return hashed_password

def check_password(password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

async def create_user(username: str, password: str):
    hashed_password = hash_password(password)
    user_doc = {
        "username": username,
        "password": hashed_password
    }
    result = await users_collection.insert_one(user_doc)
    user_doc["_id"] = result.inserted_id
    return user_doc

async def get_user(username: str):
    user = await users_collection.find_one({"username": username})
    return user

async def all_users():
    return users_collection(users = await users_collection.find().to_list(10))

async def user_history(username: str):
    history = await data_collection.find({"username": username}).to_list(10)
    return history

async def create_data(data: dict):
    result = await data_collection.insert_one(data)
    return str(result.inserted_id)

async def check_history(username: str, address: str):
    record = await data_collection.find_one({"username": username, "address": address})
    if record:
        return True
    return False