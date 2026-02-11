from fastapi import FastAPI
from skelet import imposter

app = FastAPI()

@app.get("/")
def read_root():
    return {"status": "Def noob API"}

@app.get("/get-roles")
def game_roles():
    players=['rob','hog', 'ebenya']
    result=imposter(players)
    return result

