import json
import os
import numpy as np

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_PATH = os.path.join(
    os.path.dirname(__file__),
    "..",
    "q-vercel-latency.json",
)

with open(DATA_PATH, "r", encoding="utf-8") as f:
    DATA = json.load(f)


@app.middleware("http")
async def ensure_cors_headers(request, call_next):
    response = await call_next(request)
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "*"
    return response


class Req(BaseModel):
    regions: List[str]
    threshold_ms: float


@app.post("/api/latency")
def latency(req: Req):
    out = {}

    for r in req.regions:
        rows = [x for x in DATA if x["region"] == r]

        lat = np.array(
            [x["latency_ms"] for x in rows],
            dtype=float,
        )

        up = np.array(
            [x["uptime_pct"] for x in rows],
            dtype=float,
        )

        out[r] = {
            "avg_latency": float(lat.mean()) if len(lat) else 0,
            "p95_latency": float(np.percentile(lat, 95)) if len(lat) else 0,
            "avg_uptime": float(up.mean()) if len(up) else 0,
            "breaches": int((lat > req.threshold_ms).sum()),
        }

    return {"regions": out}
