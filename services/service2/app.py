from fastapi import FastAPI
import logging

# logging simple a stdout
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("service2")

app = FastAPI(title="service2")

@app.get("/health")
def health():
    log.info("health_ok")
    return {"status": "ok", "service": "service2"}

@app.get("/hello")
def hello(name: str = "world"):
    log.info(f"hello_called name={name}")
    return {"message": f"hello {name}", "service": "service2"}
