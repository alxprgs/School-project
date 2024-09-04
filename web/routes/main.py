from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.responses import RedirectResponse, JSONResponse, HTMLResponse
from web import app, database, templates
from web.functions import *
import secrets
import pymongo


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    # Проверка авторизации пользователя
    if not UserManager.check_auth(request=request):
        return RedirectResponse("/login")

    # Список доступов, названия и ссылки
    permissions = {
        "turret": ("Автоматическая турель", "/turret"),
        "school_project": ("Школьный проект", "/school_project"),
        "diary_gdz": ("Дневник с ответами", "/diary_gdz"),
        "api": ("API", "/api_docs")
    }

    # Формируем список с информацией о доступах и цветами обводки кнопок
    access_list = []
    for key, (name, link) in permissions.items():
        has_access = UserManager.check_access(request, key)
        access_list.append({
            "name": name,
            "link": link if has_access else "#",  # Если нет доступа, ссылка ведет на текущую страницу
            "color": "green" if has_access else "red"
        })

    # Передаем данные в шаблон
    return templates.TemplateResponse("index.html", {"request": request, "access_list": access_list})

    
@app.get("/access_list", response_class=JSONResponse)
async def get_access_list(request: Request):
    if not UserManager.check_auth(request=request):
        return RedirectResponse("/login")

    permissions = {
        "turret": ("Автоматическая турель", "/turret"),
        "school_project": ("Школьный проект", "/school_project"),
        "diary_gdz": ("Дневник с ответами", "/diary_gdz"),
        "api": ("API", "/api_docs")
    }

    access_list = {}
    for key, (name, link) in permissions.items():
        if UserManager.check_access(request, key):
            access_list[key] = {"name": name, "link": link}
        else:
            access_list[key] = {"name": "Недоступно", "link": None}
    
    return access_list
