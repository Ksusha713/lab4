from fastapi import FastAPI, Request, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import fastapi.templating
from typing_extensions import Annotated
from motor.motor_asyncio import AsyncIOMotorClient
from data.db import create_data, create_user, check_password,  get_user, user_history, check_history
import httpx
from datetime import datetime

app = FastAPI()
MONGO_URL = "mongodb://127.0.0.1:27017"
client = AsyncIOMotorClient(MONGO_URL)
db = client.ip
users_collection = db.get_collection("users")
data_collection = db.get_collection("data")

templates = fastapi.templating.Jinja2Templates(directory = "templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class = HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse(
        request = request, name = "index.html"
    )

class SignUpForm(BaseModel):
    username: str   
    password: str
    repeat_password: str

class LoginForm(BaseModel):
    username: str   
    password: str

@app.get("/login", response_class=HTMLResponse)
async def login_dashboard(request: Request):
    return templates.TemplateResponse(
        request=request, name="login.html"
    )
    
@app.get("/signup", response_class=HTMLResponse)
async def signup_dashboard(request: Request):
    return templates.TemplateResponse(
        request=request, name="signup.html"
    )
    
@app.post("/signup")
async def signup(data: Annotated[SignUpForm, Form()], request: Request):
    if len(data.password) < 8:
        return templates.TemplateResponse(
            request=request, name="signup.html", context={"error": "Password is too short!"}
        )
    if data.password != data.repeat_password:
        return templates.TemplateResponse(
            request=request, name="signup.html", context={"error": "Passwords do not match!"}
        )
    already_user = await get_user(data.username)
    if already_user:
        return templates.TemplateResponse(
            request=request, name="signup.html", context={"error": "Username is already taken!"}
        )
    await create_user(data.username, data.password)
    print(f"New user registered! {data.username}")
    return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)

@app.post("/login")
async def login(data: Annotated[LoginForm, Form()], request: Request):
    user = await get_user(data.username)
    if not user:
        return templates.TemplateResponse(
            request=request, name="login.html", context={"error": "The username doesn't exist. Try to sign up!"}
        )
    if not check_password(data.password, user["password"]):
        return templates.TemplateResponse(
            request=request, name="login.html", context={"error": "The username or password is not correct!"}
        )
    response = RedirectResponse(url="/user", status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie(key="user", value=user["username"])
    return response


@app.get("/user")
async def user_dashboard(request: Request):
    user_data = request.cookies.get("user")
    if not user_data:
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
    
    client_ip = request.client.host if request.client else None
    if client_ip == "127.0.0.1" or client_ip == "::1":
        client_ip = "14.139.236.222"
    location_info = {"country": "Unknown", "city": "Unknown", "lat": "Unknown", "lon": "Unknown", "timezone": "Unknown"}
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"http://ip-api.com/json/{client_ip}")
            if response.status_code == 200:
                geo_data = response.json()
                if geo_data.get("status") == "success":
                    location_info = {
                        "country": geo_data.get("country", "Unknown"),
                        "city": geo_data.get("city", "Unknown"),
                        "lat": str(geo_data.get("lat", "Unknown")),
                        "lon": str(geo_data.get("lon", "Unknown")),
                        "timezone": geo_data.get("timezone", "Unknown")
                    }
                else:
                    location_info = {"country": "Unknown", "city": "Unknown", "lat": "Unknown", "lon": "Unknown", "timezone": "Unknown"}
    except Exception as e:
        print(f"API error: {e}")
    data = {
        "address": client_ip,
        "username": user_data,
        "time": datetime.now(),
        "geolocation": location_info
    }
    if not await check_history(user_data, client_ip):
        await create_data(data)
    history = await user_history(user_data)
    return templates.TemplateResponse("results.html", {"request": request, "user_data": user_data, "client_ip": client_ip, "location_info": location_info, "user_history": history})
    