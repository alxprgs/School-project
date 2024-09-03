from fastapi import requests, Request
from fastapi.responses import *

from web import app, database
from web.functions import *

import secrets
import pymongo

@app.get("/auth/callback/password")
async def callback_password(request: Request, response: Response):
    form_data = await request.form()
    username = form_data.get("username")
    password = form_data.get("password")
    user = database["users"].find_one({"username": username})
    if user:
        password = ServerManager.create_hash(password)
        if password == user["password"]:
            token = secrets.token_urlsafe(256)
            try:
                database["users"].update_one(
                    {"_id": user["_id"]},
                    {"$set": {"session": {"token": token}}}
                )
                response = RedirectResponse(url="/")
                response.set_cookie(key="auth_token", value=token)
                response.set_cookie(key="auth", value=True)
                response.set_cookie(key="auth_type", value="Password")
                return response
            except pymongo.errors.WriteError as e:
                return JSONResponse({"status": False, "message": str(e)})
        else:
            return JSONResponse({"status": False, "message": "Неверный пароль"})
    else:
        return JSONResponse({"status": False, "message": "Пользователь не найден."})