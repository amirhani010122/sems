from pydantic import BaseModel, EmailStr


class UserRegister(BaseModel):
    email: str
    username: str
    password: str


class UserLogin(BaseModel):
    email: str
    password: str
    
# {
#     emaIl: "amir@test.com",
#     password : "123"
# }

class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: str = None
