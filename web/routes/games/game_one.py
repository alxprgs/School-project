from fastapi import *
from fastapi.responses import *
from web import app, database, templates, fs
from web.functions import *
import secrets
import pymongo
from bson import ObjectId
import io

@app.get("/games_one", response_class=HTMLResponse)
async def game_one(request = Request):
    content = templates.TemplateResponse("games/game_one_start.py", {"request": request})
    return content

@app.get(f"/games_one/page", response_class=HTMLResponse)
async def game_one_page(request: Request, page_name: str):
    config = ConfigManager.open_config("configs/game_one.json")
    background_image_url = config[page_name]["background_image_url"]
    button1_text = config[page_name]["button1_text"]
    button2_text = config[page_name]["button2_text"]
    page_title = config[page_name]["page_title"]
    content = templates.TemplateResponse("games/game_one.py", 
                                        {"request": request,
                                        "page_title": page_title,
                                        "background_image_url": background_image_url,
                                        "button1_text": button1_text,
                                        "button2_text": button2_text})
    return content