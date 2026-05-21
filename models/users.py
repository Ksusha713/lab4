from pydantic import BaseModel

class Users(BaseModel):
    username: str
    hashed_password: str


    