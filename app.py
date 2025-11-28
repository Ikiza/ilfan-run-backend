from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import httpx
import os

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

GH_KEY = os.environ.get("GRAPHHOPPER_KEY")
GH_URL = "https://graphhopper.com/api/1/route"

@app.get("/route")
async def route(startLat: float, startLon: float, endLat: float, endLon: float):
    if not GH_KEY:
        raise HTTPException(status_code=500, detail="GRAPHHOPPER_KEY not set")

    payload = {
        "profile": "foot",
        "points_encoded": False,
        "instructions": False,
        "points": [
            [startLon, startLat],
            [endLon, endLat],
        ],
    }

    async with httpx.AsyncClient(timeout=20) as client:
        r = await client.post(GH_URL, params={"key": GH_KEY}, json=payload)
    if r.status_code != 200:
        raise HTTPException(status_code=500, detail=f"GraphHopper error: {r.text}")

    data = r.json()
    path = data["paths"][0]
    return {
        "distance_m": path["distance"],
        "time_ms": path["time"],
        "geojson": {
            "type": "Feature",
            "geometry": path["points"],
            "properties": {},
        },
    }
