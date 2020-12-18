from fastapi import FastAPI, Request, UploadFile, File
from fastapi.templating import Jinja2Templates
import os
import shutil
import uvicorn
import tracemoepy
import asyncio

app = FastAPI()
templates = Jinja2Templates(directory="src/templates")
tracemoe = tracemoepy.tracemoe.TraceMoe()

@app.get("/")
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/sauce")
def sauce(image: UploadFile = File(...)):
    
    temp_file = _save_file_to_disk(image, path="temp", save_as="temp")
    data = get_data(temp_file)
    print(data["RawDocsCount"])
    return {"title": str(data["RawDocsCount"]), "all": data}


def _save_file_to_disk(uploaded_file, path=".", save_as="default"):
    extension = os.path.splitext(uploaded_file.filename)[-1]
    temp_file = os.path.join(path, save_as + extension)
    with open(temp_file, "wb") as buffer:
        shutil.copyfileobj(uploaded_file.file, buffer)
    return temp_file

def get_data(image):
    return tracemoe.search(image, encode=True)


if __name__ == "__main__":
    uvicorn.run("base:app", port=8000, reload=True)