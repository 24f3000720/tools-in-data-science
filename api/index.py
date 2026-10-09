import json, os
import numpy as np
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
DATA = json.load(open(os.path.join(os.path.dirname(__file__), "..", "q-vercel-latency.json")))

class Req(BaseModel):
    regions: List[str]
    threshold_ms: float

@app.post("/api/latency")
def latency(req: Req):
    out = {}
    for r in req.regions:
        rows = [x for x in DATA if x["region"] == r]
        lat = np.array([x["latency_ms"] for x in rows], dtype=float)
        up = np.array([x["uptime_pct"] for x in rows], dtype=float)
        out[r] = {"avg_latency": float(lat.mean()), "p95_latency": float(np.percentile(lat, 95)),
                  "avg_uptime": float(up.mean()), "breaches": int((lat > req.threshold_ms).sum())}
    return out
