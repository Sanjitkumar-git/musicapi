from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from ytmusicapi import YTMusic
import yt_dlp

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

yt = YTMusic()

@app.get("/search_with_audio")
def search_with_audio(q: str, limit: int = 20):
    results = yt.search(q, filter="songs", limit=limit)
    songs = []
    for item in results:
        songs.append({
            "id": item['videoId'],
            "title": item['title'],
            "artist": item['artists'][0]['name'] if item.get('artists') else "Unknown",
            "thumbnail": item['thumbnails'][-1]['url'] if item.get('thumbnails') else "",
            "audioUrl": f"https://your-backend.com/stream/{item['videoId']}"  # Point to stream endpoint
        })
    return {"success": True, "data": songs}

@app.get("/stream/{video_id}")
def get_audio_stream(video_id: str):
    try:
        # Use yt-dlp to get direct audio URL
        ydl_opts = {
            'format': 'bestaudio/best',
            'quiet': True,
            'no_warnings': True,
            'extract_flat': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"https://www.youtube.com/watch?v={video_id}", download=False)
            # Get best audio format URL
            if 'url' in info:
                audio_url = info['url']
            elif 'formats' in info:
                audio_formats = [f for f in info['formats'] if f.get('acodec') != 'none']
                if audio_formats:
                    audio_url = audio_formats[-1]['url']
                else:
                    audio_url = f"https://www.youtube.com/watch?v={video_id}"
            else:
                audio_url = f"https://www.youtube.com/watch?v={video_id}"
        
        return {"success": True, "audioUrl": audio_url}
    except Exception as e:
        return {"success": False, "error": str(e), "audioUrl": f"https://www.youtube.com/watch?v={video_id}"}
