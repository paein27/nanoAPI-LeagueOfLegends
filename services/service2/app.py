import time, uuid, logging
from typing import List
from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel

SERVICE_NAME = "service2"

# ---------- logging JSON a stdout ----------
logger = logging.getLogger(SERVICE_NAME)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
logger.handlers = [handler]
logger.propagate = False

app = FastAPI(title=SERVICE_NAME, version="1.0.0")

# ---------- middleware de request logging ----------
@app.middleware("http")
async def log_requests(request: Request, call_next):
    rid = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    start = time.perf_counter()
    try:
        resp: Response = await call_next(request)
    except Exception:
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

# ---------- datos + endpoint único ----------
class Player(BaseModel):
    nick: str
    role: str
    years: str  # rango legible (no exhaustivo)

PLAYERS: List[Player] = [
    Player(nick="Faker",    role="Mid",     years="2013–presente"),
    Player(nick="Bengi",    role="Jungle",  years="2013–2016, 2019"),
    Player(nick="Impact",   role="Top",     years="2013–2014"),
    Player(nick="Piglet",   role="ADC",     years="2013–2014"),
    Player(nick="PoohManDu",role="Support", years="2013–2014"),
    Player(nick="MaRin",    role="Top",     years="2014–2015"),
    Player(nick="Easyhoon", role="Mid",     years="2014–2015"),
    Player(nick="Bang",     role="ADC",     years="2013–2018"),
    Player(nick="Wolf",     role="Support", years="2013–2018"),
    Player(nick="Duke",     role="Top",     years="2016"),
    Player(nick="Blank",    role="Jungle",  years="2016–2018"),
    Player(nick="Huni",     role="Top",     years="2017"),
    Player(nick="Peanut",   role="Jungle",  years="2017"),
    Player(nick="Untara",   role="Top",     years="2017–2018"),
    Player(nick="Profit",   role="Top",     years="2017"),
    Player(nick="Effort",   role="Support", years="2019–2020"),
    Player(nick="Teddy",    role="ADC",     years="2019–2021"),
    Player(nick="Mata",     role="Support", years="2019"),
    Player(nick="Khan",     role="Top",     years="2019"),
    Player(nick="Clid",     role="Jungle",  years="2019"),
    Player(nick="Canna",    role="Top",     years="2020–2021"),
    Player(nick="Cuzz",     role="Jungle",  years="2020–2021"),
    Player(nick="Gumayusi", role="ADC",     years="2020–presente"),
    Player(nick="Keria",    role="Support", years="2021–presente"),
    Player(nick="Oner",     role="Jungle",  years="2021–presente"),
    Player(nick="Zeus",     role="Top",     years="2022–presente"),
]

@app.get("/players", response_model=List[Player])
def list_players():
    """
    ÚNICO método GET del microservicio:
    Devuelve una lista (no exhaustiva) de jugadores que han pasado por T1.
    """
    logger.info("players_listed", extra={"service": SERVICE_NAME, "count": len(PLAYERS)})
    return PLAYERS
