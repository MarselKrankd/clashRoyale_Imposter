from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.api import auth, game, websocket
from app.services.db_card import seed_cards

app = FastAPI(title="Clash Royale Imposter")

seed_cards()

app.mount("/static", StaticFiles(directory="static"), name="static")


app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(game.router, prefix="/game", tags=["Game"])
app.include_router(websocket.router, tags=["Websocket"])

@app.get("/", tags=["System"])
def read_root():
    return {"status": "running", "mode": "def noob api"}