from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from ytmusicapi import YTMusic
from typing import Optional
import re

app = FastAPI()

# CORS for Flutter app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

yt = YTMusic()

@app.get("/")
def home():
    return {"message": "YT Music backend running"}

# 🔍 Search songs (with videoId)
@app.get("/search/{song}")
def search(song: str, limit: int = 20):
    try:
        results = yt.search(song, filter="songs", limit=limit)
        
        songs = []
        for item in results:
            songs.append({
                "videoId": item['videoId'],
                "title": item['title'],
                "artists": item['artists'][0]['name'] if item.get('artists') else "Unknown",
                "thumbnail": item['thumbnails'][-1]['url'] if item.get('thumbnails') else "",
                "duration": item.get('duration'),
            })
        
        return {"success": True, "data": songs}
    except Exception as e:
        return {"success": False, "error": str(e)}

# 🎵 GET AUDIO STREAM URL - YAHI SE SONG PLAY HOGA
@app.get("/stream/{video_id}")
def get_stream(video_id: str):
    try:
        # Method 1: Get watch playlist
        watch_playlist = yt.get_watch_playlist(video_id)
        
        if watch_playlist and watch_playlist.get('tracks'):
            track = watch_playlist['tracks'][0]
            
            # Try to get stream URL
            if track.get('videoDetails') and track['videoDetails'].get('videoId'):
                # Alternative method
                try:
                    # Get streaming data
                    stream_data = yt.get_audio_stream(video_id)
                    if stream_data:
                        return {"success": True, "audioUrl": stream_data['url']}
                except:
                    pass
            
            # Fallback: Use watch URL (just_audio can handle)
            watch_url = f"https://www.youtube.com/watch?v={video_id}"
            return {"success": True, "audioUrl": watch_url}
        
        return {"success": False, "error": "Stream not found"}
        
    except Exception as e:
        return {"success": False, "error": str(e)}

# 🎯 Search and get direct audio URLs in one call
@app.get("/search_with_audio")
def search_with_audio(q: str = Query(...), limit: int = 10):
    try:
        results = yt.search(q, filter="songs", limit=limit)
        
        songs = []
        for item in results:
            video_id = item['videoId']
            
            # Get audio URL for each song
            audio_url = None
            try:
                watch_playlist = yt.get_watch_playlist(video_id)
                if watch_playlist and watch_playlist.get('tracks'):
                    audio_url = f"https://www.youtube.com/watch?v={video_id}"
            except:
                pass
            
            songs.append({
                "id": video_id,
                "title": item['title'],
                "artist": item['artists'][0]['name'] if item.get('artists') else "Unknown",
                "thumbnail": item['thumbnails'][-1]['url'] if item.get('thumbnails') else "",
                "audioUrl": audio_url,
            })
        
        return {"success": True, "data": songs}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/artists/{name}")
def artists(name: str):
    try:
        results = yt.search(name, filter="artists", limit=5)
        return {"success": True, "data": results}
    except Exception as e:
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
