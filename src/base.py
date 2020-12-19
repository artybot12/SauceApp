from fastapi import FastAPI, Request, UploadFile, File
from fastapi.templating import Jinja2Templates
import os
import shutil
import uvicorn
import tracemoepy
import asyncio
import requests

app = FastAPI()
templates = Jinja2Templates(directory="src/templates")
tracemoe = tracemoepy.tracemoe.TraceMoe()

@app.get("/")
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/sauce")
def sauce(image: UploadFile = File(...)): 
    temp_file = _save_file_to_disk(image, path="temp", save_as="temp")
    if not temp_file:
        return
    data = get_data(temp_file)['docs'][0]

    return {"title": data["title_english"],
            "title2": data["title_romaji"],
            "season": data["season"],
            "episode": data["episode"],
            "time": getTime(data['at']),
            "sim": getSim(str(data["similarity"])),
            "preview": getPreview(data)
            }

def getPreview(data: dict):
    uriEncoded = requests.utils.quote(data['filename'])
    preview = "https://trace.moe/thumbnail.php?anilist_id=" + str(
                data['anilist_id']) + "&file=" + uriEncoded.replace(" ", "") + "&t=" + str(
                    data['at']) + "&token=" + str(data['tokenthumb'])
    return preview

def getTime(at: str):
    p1, p2 = float(at) % 60,  float(at) / 60
    p3, p2 = p2 % 60, p2 / 60
    return str(int(p2)) + ":" + str(int(p3)) + ":" + str(int(p1))


def getSim(sim: str):
    return float(sim[0:4]) * 100


def _save_file_to_disk(uploaded_file, path=".", save_as="default"):
    extension = os.path.splitext(uploaded_file.filename)[-1]
    if extension in {"png", "jpeg"}:
        temp_file = os.path.join(path, save_as + extension)
        with open(temp_file, "wb") as buffer:
            shutil.copyfileobj(uploaded_file.file, buffer)
        return temp_file
    return 


def get_data(image):
    return tracemoe.search(image, encode=True)


if __name__ == "__main__":
    uvicorn.run("base:app", port=8000, reload=True)