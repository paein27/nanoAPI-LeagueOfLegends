import time, uuid, logging
from typing import List, Optional
from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from pythonjsonlogger import jsonlogger

# -------------------------
# Logger JSON a stdout
# -------------------------
SERVICE_NAME = "service1"

logger = logging.getLogger(SERVICE_NAME)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(jsonlogger.JsonFormatter(
    "%(asctime)s %(levelname)s %(name)s %(message)s %(service)s %(request_id)s %(path)s %(method)s %(status_code)s %(elapsed_ms)s"
))
logger.handlers = [handler]
logger.propagate = False

# -------------------------
# Datos de ejemplo (subset)
# Puedes ampliar la lista
# -------------------------
class Champion(BaseModel):
    slug: str
    name: str
    roles: List[str]

CHAMPIONS: List[Champion] = [
    Champion(slug="aatrox", name="Aatrox", roles=["Top"]),
    Champion(slug="ahri", name="Ahri", roles=["Mid"]),
    Champion(slug="akali", name="Akali", roles=["Mid", "Top"]),
    Champion(slug="alistar", name="Alistar", roles=["Support"]),
    Champion(slug="ashe", name="Ashe", roles=["ADC"]),
    Champion(slug="blitzcrank", name="Blitzcrank", roles=["Support"]),
    Champion(slug="caitlyn", name="Caitlyn", roles=["ADC"]),
    Champion(slug="darius", name="Darius", roles=["Top"]),
    Champion(slug="evelynn", name="Evelynn", roles=["Jungle"]),
    Champion(slug="ezreal", name="Ezreal", roles=["ADC", "Mid"]),
    Champion(slug="fiora", name="Fiora", roles=["Top"]),
    Champion(slug="garen", name="Garen", roles=["Top"]),
    Champion(slug="ivern", name="Ivern", roles=["Jungle"]),
    Champion(slug="jax", name="Jax", roles=["Top", "Jungle"]),
    Champion(slug="jinx", name="Jinx", roles=["ADC"]),
    Champion(slug="kaisa", name="Kai'Sa", roles=["ADC"]),
    Champion(slug="katarina", name="Katarina", roles=["Mid"]),
    Champion(slug="leesin", name="Lee Sin", roles=["Jungle"]),
    Champion(slug="leona", name="Leona", roles=["Support"]),
    Champion(slug="lux", name="Lux", roles=["Mid", "Support"]),
    Champion(slug="malphite", name="Malphite", roles=["Top"]),
    Champion(slug="morgana", name="Morgana", roles=["Support", "Mid"]),
    Champion(slug="nasus", name="Nasus", roles=["Top"]),
    Champion(slug="nidalee", name="Nidalee", roles=["Jungle", "Mid"]),
    Champion(slug="riven", name="Riven", roles=["Top"]),
    Champion(slug="senna", name="Senna", roles=["ADC", "Support"]),
    Champion(slug="sett", name="Sett", roles=["Top", "Jungle"]),
    Champion(slug="soraka", name="Soraka", roles=["Support"]),
    Champion(slug="thresh", name="Thresh", roles=["Support"]),
    Champion(slug="vayne", name="Vayne", roles=["ADC"]),
    Champion(slug="vi", name="Vi", roles=["Jungle"]),
    Champion(slug="viktor", name="Viktor", roles=["Mid"]),
    Champion(slug="yasuo", name="Yasuo", roles=["Mid", "Top"]),
    Champion(slug="yone", name="Yone", roles=["Mid", "Top"]),
    Champion(slug="zed", name="Zed", roles=["Mid"]),
]

app = FastAPI(title=SERVICE_NAME, version="1.0.0")

# -------------------------
# Middleware: logging por request (con request_id)
# -------------------------
@app.middleware("http")
async def log_requests(request: Request, call_next):
    rid = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    start = time.perf_counter()
    try:
        resp: Response = await call_next(request)
    except Exception as exc:
        elapsed = int((time.perf_counter() - start) * 1000)
        logger.error("request_error", extra={
            "service": SERVICE_NAME, "request_id": rid,
            "path": request.url.path, "method": request.method,
            "status_code": 500, "elapsed_ms": elapsed
        })
        return JSONResponse(status_code=500, content={"error": "internal_error"})
    elapsed = int((time.perf_counter() - start) * 1000)
    logger.info("request_ok", extra={
        "service": SERVICE_NAME, "request_id": rid,
        "path": request.url.path, "method": request.method,
        "status_code": resp.status_code, "elapsed_ms": elapsed
    })
    resp.headers["X-Request-ID"] = rid
    return resp

# -------------------------
# Endpoints
# -------------------------
@app.get("/health")
def health():
    logger.info("health_ok", extra={"service": SERVICE_NAME})
    return {"status": "ok", "service": SERVICE_NAME}

@app.get("/champions", response_model=List[Champion])
def list_champions(role: Optional[str] = None, q: Optional[str] = None, limit: int = 100, offset: int = 0):
    """
    - role: filtra por rol (ej: Top, Jungle, Mid, ADC, Support)
    - q: busca por nombre parcial (case-insensitive)
    - limit/offset: paginación simple
    """
    data = CHAMPIONS
    if role:
        role_norm = role.strip().lower()
        data = [c for c in data if any(r.lower() == role_norm for r in c.roles)]
    if q:
        q_norm = q.strip().lower()
        data = [c for c in data if q_norm in c.name.lower()]
    result = data[offset: offset + max(0, min(limit, 200))]
    logger.info("champions_listed", extra={"service": SERVICE_NAME, "count": len(result), "role": role, "q": q})
    return result

@app.get("/champions/{slug}", response_model=Champion)
def get_champion(slug: str):
    for c in CHAMPIONS:
        if c.slug == slug.lower():
            logger.info("champion_found", extra={"service": SERVICE_NAME, "slug": slug})
            return c
    logger.info("champion_not_found", extra={"service": SERVICE_NAME, "slug": slug})
    raise HTTPException(status_code=404, detail="champion_not_found")
