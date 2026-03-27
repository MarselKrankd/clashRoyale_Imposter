from pydantic import BaseModel, Field
from typing import List

class UserData(BaseModel):
    name: str = Field(..., min_length=3, max_length=20, example="Marsel")
    password: str = Field(..., min_length=5, example="lolKek21")

class PlayersList(BaseModel):
    players_list: List[str]

class RoomCreateRequest(BaseModel):
    player_id: str

class JoinRoomRequest(BaseModel):
    player_id: str
    password: str
    room_id: str

class LeaveRoomRequest(BaseModel):
    player_id: str
    room_id: str