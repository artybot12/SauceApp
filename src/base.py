from fastapi import FastAPI, Request, UploadFile, File, Form
from fastapi.templating import Jinja2Templates
import os
import shutil
import uvicorn
import tracemoepy
import asyncio
import requests
import time

app = FastAPI()
templates = Jinja2Templates(directory="src/templates")
tracemoe = tracemoepy.tracemoe.TraceMoe()


@app.get("/")
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/full")
async def full(title: str = Form(...)):
    try:
        args = title.replace(" ", "%20")
        url = "https://api.jikan.moe/v3/search/anime?q=" + args + "&limit=1"
        r = await get_data_2(url)
        data = r.json()
        data = data['results'][0]

        return {"success": "400",
                "url": data["url"],
                "image_url": data["image_url"],
                "title": data["title"],
                "airing": data["airing"],
                "synopsis": data["synopsis"],
                "type": data["type"],
                "episodes": data["episodes"],
                "score": data["score"],
                "start_date": data["start_date"][:10],
                "end_date": data["end_date"][:10],
                "rated": data["rated"]
                }
    except Exception:
        return


@app.post("/sauce")
async def sauce(image: UploadFile = File(...)): 
    temp_file = _save_file_to_disk(image, path="temp", save_as="temp")

    if not temp_file:
        return

    data = await get_data(temp_file)
    data = data['docs'][0]

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
    return time.strftime('%H:%M:%S', time.gmtime(int(at)))


def getSim(sim: str):
    return float(sim[:4]) * 100


def _save_file_to_disk(uploaded_file, path=".", save_as="default"):
    extension = os.path.splitext(uploaded_file.filename)[-1]
    if extension in {".png", ".jpeg", '.jpg'}:
        temp_file = os.path.join(path, save_as + extension)
        with open(temp_file, "wb") as buffer:
            shutil.copyfileobj(uploaded_file.file, buffer)
        return temp_file
    return 


async def get_data(image: object):
    return tracemoe.search(image, encode=True)


async def get_data_2(url: str):
    return requests.get(url)


if __name__ == "__main__":
    uvicorn.run("base:app", port=8000, reload=True)