from pydantic import BaseModel, Field
from typing import List, Optional

class PlayerRoleResponse(BaseModel):
    status: str = Field(..., example="active") 
    role: Optional[str] = Field(None, example="Player") 
    card_name: Optional[str] = Field(None, example="Всадник на кабане")
    image_url: Optional[str] = Field(None, example="/static/cards/Hog.webp")
    elixir: Optional[int] = Field(None, example=4)

    class Config:
        from_attributes = True

class UserAuthResponse(BaseModel):
    status: str
    player_id: str
    username: str

class RoomCreateResponse(BaseModel):
    room_id: str
    room_name: str
    password: str
    host_name: str

class SimpleStatusResponse(BaseModel): 
    status: str

class UserData(BaseModel):
    name: str = Field(..., min_length=3, max_length=20, example="Marsel")
    password: str = Field(..., min_length=5, example="lolKek21")



class RoomCreateRequest(BaseModel):
    player_id: str
    room_name: str = Field(..., min_length=1, max_length=30, example="КрутыеБобры")

class JoinRoomRequest(BaseModel):
    player_id: str
    room_id: str  
    password: str 

class LeaveRoomRequest(BaseModel):
    player_id: str
    room_id: str


class PlayerInfo(BaseModel):
    name: str
    player_id: str

class RoomParticipantsResponse(BaseModel):
    room_id: str
    count: int
    players: List[PlayerInfo]

class RoomListResponse(BaseModel):
    room_id: str
    room_name: str
    host_id: str


class PlayersList(BaseModel):
    players_list: List[str]