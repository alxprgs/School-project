import pymongo
import gridfs

from fastapi.staticfiles import StaticFiles
from fastapi import *
from fastapi.responses import *
from fastapi.templating import Jinja2Templates

from web.functions import *

app = FastAPI(version="Beta 1.0 | Build 03.09.2024",
              debug=True,)
config = ConfigManager.open_config()

app.mount("/static", StaticFiles(directory="web/static"), name="static")
app.mount("/templates", StaticFiles(directory="web/templates"), name="templates")
app.mount("/temp", StaticFiles(directory="web/temp"), name="temp")
templates = Jinja2Templates(directory="web/templates")

client = pymongo.MongoClient(config["setup"]["databases"]["mongodb_link"])
database = client["site"]
fs = gridfs.GridFS(database=database)

from web.routes.auth import backend
from web.routes import main, diary_gdz