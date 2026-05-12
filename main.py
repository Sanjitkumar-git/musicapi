from fastapi import FastAPI
from ytmusicapi import YTMusic

app = FastAPI()
yt = YTMusic()

@app.get("/")
def home():
    return {"message": "YT Music backend running"}

@app.get("/search/{song}")
def search(song: str):
    return yt.search(song, filter="songs")[:10]

@app.get("/artists/{name}")
def artists(name: str):
    return yt.search(name, filter="artists")[:5]