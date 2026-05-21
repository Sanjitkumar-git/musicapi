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
        video_id = item['videoId']
        
        # 🔥 Direct audio URL fetch karo
        audio_url = get_direct_audio_url(video_id)
        
        songs.append({
            "id": video_id,
            "title": item['title'],
            "artist": item['artists'][0]['name'] if item.get('artists') else "Unknown",
            "thumbnail": item['thumbnails'][-1]['url'] if item.get('thumbnails') else "",
            "audioUrl": audio_url  # 🔥 Direct audio URL
        })
    return {"success": True, "data": songs}

def get_direct_audio_url(video_id: str):
    try:
        ydl_opts = {
            'format': 'bestaudio/best',
            'quiet': True,
            'no_warnings': True,
            'extract_flat': True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"https://www.youtube.com/watch?v={video_id}", download=False)
            # Best audio format URL
            for f in info.get('formats', []):
                if f.get('acodec') != 'none' and 'audio' in f.get('format_note', '').lower():
                    return f.get('url')
            return None
    except:
        return None
