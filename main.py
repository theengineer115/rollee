from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.responses import JSONResponse

# import functions that return data
from web_scraping import LoginUser, UserInfo

# handle the two possible request bodies
class UsernamePassword(BaseModel):
    username: str
    password: str

class AuthToken(BaseModel):
    token: str

# initialize app
app = FastAPI()

# auth endpoint
@app.post("/auth")
async def auth(username_password: UsernamePassword):
    # get token and save logins to python in memory dict
    token = LoginUser(username_password.username, username_password.password)
    # if invalid token
    if token == "":
        return JSONResponse(content={"error": "invalid username or password"}, status_code=400)
    # return token
    return {"token": token}

# pull endpoint
@app.post("/pull")
async def pull(token: AuthToken):
    # get user info given the token
    user_info = UserInfo(token.token)
    # if invalid info
    if user_info == {}:
        return JSONResponse(content={"error": "invalid token"}, status_code=400)
    # return user info
    return JSONResponse(content=user_info)

# fetch endpoint
@app.post("/fetch")
async def fetch(username_password: UsernamePassword):
    # combine the logic from the two previous functions
    token = LoginUser(username_password.username, username_password.password)
    if token == "":
        return JSONResponse(content={"error": "invalid username or password"}, status_code=400)
    user_info = UserInfo(token)
    return JSONResponse(content=user_info)
