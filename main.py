from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from app.api import auth, game, websocket
from app.services.db_card import seed_cards

BASE_DIR = Path(__file__).resolve().parent  
FRONT_DIR = BASE_DIR / "static" / "frontend"
ASSETS_DIR = FRONT_DIR / "assets"
INDEX_FILE = FRONT_DIR / "index.html"

app = FastAPI(title="Clash Royale Imposter")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

seed_cards()

app.mount("/app/assets", StaticFiles(directory=str(ASSETS_DIR)), name="frontend-assets")

@app.get("/app")

@app.get("/app/")
async def app_index():
    return FileResponse(str(INDEX_FILE))

@app.get("/app/{full_path:path}")
async def app_spa(full_path: str):
    return FileResponse(str(INDEX_FILE))

app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(game.router, prefix="/game", tags=["Game"])
app.include_router(websocket.router, tags=["Websocket"])

@app.get("/", tags=["System"])
def read_root():
    return {"status": "running", "mode": "def noob api"}