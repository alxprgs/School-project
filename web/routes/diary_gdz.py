from fastapi import *
from fastapi.responses import *
from web import app, database, templates, fs
from web.functions import *
import secrets
import pymongo
from bson import ObjectId
import io

@app.get("/diary_gdz", response_class=HTMLResponse)
async def main():
    content = """
    <html>
        <body>
            <h1>Загрузить фото</h1>
            <form action="/diary_gdz/upload" method="post" enctype="multipart/form-data">
                <input type="file" name="files" multiple>
                <button type="submit">Загрузить</button>
            </form>
        </body>
    </html>
    """
    return content

@app.post("/diary_gdz/upload")
async def upload_files(files: list[UploadFile] = File(...)):
    file_ids = []
    for file in files:
        file_data = await file.read()
        file_id = fs.put(file_data, filename=file.filename)
        file_ids.append(str(file_id))

    return {"status": "True", "file_ids": file_ids}

@app.get("/diary_gdz/file/{file_id}")
async def get_file(file_id: str):
    try:
        file = fs.get(ObjectId(file_id))
        return StreamingResponse(io.BytesIO(file.read()), media_type='application/octet-stream', headers={"Content-Disposition": f"attachment; filename={file.filename}"})
    except Exception as e:
        return {"error": str(e)}