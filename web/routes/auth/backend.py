from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.responses import RedirectResponse, JSONResponse, HTMLResponse
from web import app, database, templates
from web.functions import *
import secrets
import pymongo


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("auth/index.html", {"request": request})

@app.post("/auth/callback/password")
async def callback_password(request: Request):
    form_data = await request.json()
    username = form_data.get("username")
    password = form_data.get("password")

    if not username or not password:
        raise HTTPException(status_code=400, detail="Имя пользователя и пароль обязательны.")
    
    user = database["users"].find_one({"username": username})
    
    if user:
        hashed_password = ServerManager.create_hash(password)
        if hashed_password == user["password"]:
            token = secrets.token_urlsafe(256)
            try:
                database["users"].update_one(
                    {"_id": user["_id"]},
                    {"$set": {"session": {"token": token}}}
                )
                response = RedirectResponse(url="/main")
                response.set_cookie(key="auth_token", value=token, httponly=True, secure=True)
                response.set_cookie(key="auth", value="true", httponly=True, secure=True)
                response.set_cookie(key="auth_type", value="Password", httponly=True, secure=True)
                return response
            except pymongo.errors.WriteError as e:
                return JSONResponse({"status": False, "message": str(e)}, status_code=500)
        else:
            return JSONResponse({"status": False, "message": "Неверный пароль"}, status_code=401)
    else:
        return JSONResponse({"status": False, "message": "Пользователь не найден."}, status_code=404)

@app.post("/auth/callback/registration")
async def registration(request: Request):
    form_data = await request.json()
    username = form_data.get("username")
    mail = form_data.get("mail")
    password = form_data.get("password")
    password_repetition = form_data.get("password_repetition")

    if not username or not mail or not password or not password_repetition:
        raise HTTPException(status_code=400, detail="Все поля обязательны.")
    
    user = database["users"].find_one({"username": username})
    
    if user:
        return JSONResponse({"status": False, "description": "Пользователь с таким логином уже существует."}, status_code=409)
    
    user = database["users"].find_one({"mail": mail})
    
    if user:
        return JSONResponse({"status": False, "description": "Пользователь с такой почтой уже существует."}, status_code=409)
    
    if password != password_repetition:
        return JSONResponse({"status": False, "description": "Пароль не соответствует повторению."}, status_code=400)
    
    try:
        hashed_password = ServerManager.create_hash(password)
        token = secrets.token_urlsafe(256)
        database["users"].insert_one({
            "username": username,
            "password": hashed_password,
            "mail": mail,
            "session": {
                "token": token
            },
            "permissions": {}
        })
        ServerManager.server_log(text=f"Удачная попытка создания пользователя '{username}'.", type=1)
        response = RedirectResponse(url="/main")
        response.set_cookie(key="auth_token", value=token, httponly=True, secure=True)
        response.set_cookie(key="auth", value="true", httponly=True, secure=True)
        response.set_cookie(key="auth_type", value="Password", httponly=True, secure=True)
        return response
    except pymongo.errors.OperationFailure as e:
        ServerManager.server_log(text=f"Неудачная попытка создания пользователя '{username}'.", type=2, e=e)
        return JSONResponse({"status": False, "description": "Ошибка сервера"}, status_code=500)
