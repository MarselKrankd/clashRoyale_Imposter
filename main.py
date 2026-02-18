from fastapi import FastAPI
from skelet import imposter
from typing import List
import random
import uuid
import string

game_rooms={}

app = FastAPI()

@app.get("/")
def read_root():
    return {"status": "Def noob API"}

@app.post("/get-roles")
def game_roles(players :List[str]):
    result=imposter(players)
    return result

@app.post("/create-room")
def create_room():
    room_id=str(uuid.uuid4())
    password="".join(random.choices(string.ascii_uppercase + string.digits, k=5))
    game_rooms[room_id] = {"password": password, "players": []}
    return {"room_id": room_id, "password": password}
    
    

