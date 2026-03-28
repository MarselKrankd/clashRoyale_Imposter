from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import uuid
import random
import string
import app.db.models as models
from app.db.session import get_db
from app.schemas.schemas import (RoomCreateRequest, JoinRoomRequest, LeaveRoomRequest, 
RoomListResponse, RoomCreateResponse, RoomParticipantsResponse, SimpleStatusResponse, PlayerRoleResponse)
from app.services.game_logic import imposter
from app.services.manager import manager
from typing import List

router = APIRouter()

def check_player(player_id: str, db: Session):
    exists = db.query(models.RoomParticipant).filter(models.RoomParticipant.player_id == player_id).first()
    if exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=f"Вы находитесь в другой комнаие (ID: {exists.room_name})"
        )


@router.get("/rooms", response_model=List[RoomListResponse])
def list_rooms(db: Session = Depends(get_db)):
    rooms = db.query(models.Room).all()
    return rooms

@router.post("/create-room", response_model=RoomCreateResponse)
def create_room(data: RoomCreateRequest, db: Session = Depends(get_db)):
    check_player(data.player_id, db)
    host = db.query(models.User).filter(models.User.player_id == data.player_id).first()
    if not host:
        raise HTTPException(status_code=404, detail="Игрок не найден")
    
    room_id = str(uuid.uuid4())
    room_password = "".join(random.choices(string.ascii_uppercase + string.digits, k=5))
    new_room = models.Room(
        room_id=room_id, 
        room_name=data.room_name, 
        room_pass=room_password, 
        host_id=host.player_id
    )
    new_participant = models.RoomParticipant(room_id=room_id, player_id=host.player_id)

    db.add(new_room)
    db.add(new_participant)
    db.commit()
    
    return {
        "room_id": room_id, 
        "room_name": data.room_name,
        "password": room_password, 
        "host_name": host.name
    }

@router.post("/join-room", response_model=SimpleStatusResponse)
def join_room(data: JoinRoomRequest, db: Session = Depends(get_db)):
    check_player(data.player_id, db)
    player = db.query(models.User).filter(models.User.player_id == data.player_id).first()
    if not player:
        raise HTTPException(status_code=404, detail="Игрок не существует")
        
    room = db.query(models.Room).filter(models.Room.room_id == data.room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Комната не найдена")
        
    if data.password != room.room_pass:
        raise HTTPException(status_code=401, detail="Неверный пароль")
        
    new_participant = models.RoomParticipant(room_id=data.room_id, player_id=data.player_id)
    db.add(new_participant)
    db.commit()
    
    return {"status": "joined"}

@router.post("/leave-room", response_model=SimpleStatusResponse)
async def leave_room(data: LeaveRoomRequest, db: Session = Depends(get_db)):
    participant = db.query(models.RoomParticipant).filter(
        models.RoomParticipant.room_id == data.room_id,
        models.RoomParticipant.player_id == data.player_id
    ).first()
    if not participant:
        raise HTTPException(status_code=404, detail="Вы не участник этой комнаты")

    room = db.query(models.Room).filter(models.Room.room_id == data.room_id).first()
    if room and room.host_id == data.player_id:
        db.query(models.RoomParticipant).filter(models.RoomParticipant.room_id == data.room_id).delete()
        db.delete(room)
        await manager.broadcast_to_room(data.room_id, {"event": "room_closed", "message": "Хост покинул игру"})
    else:
        db.delete(participant)
        await manager.broadcast_to_room(data.room_id, {"event": "player_left", "player_id": data.player_id})  
    db.commit()
    return {"status": "left"}

@router.get("/room-participants/{room_id}", response_model=RoomParticipantsResponse)
def get_participants(room_id: str, db: Session = Depends(get_db)):
    participants = db.query(models.RoomParticipant).filter(models.RoomParticipant.room_id == room_id).all()
    
    player_id = [p.player_id for p in participants]
    users = db.query(models.User).filter(models.User.player_id.in_(player_id)).all()
    
    return {
        "room_id": room_id,
        "count": len(users),
        "players": [{"name": u.name, "player_id": u.player_id} for u in users]
    }

@router.post("/game-start", response_model=SimpleStatusResponse)
async def start_game(room_id: str, player_id: str, db: Session = Depends(get_db)):
    room = db.query(models.Room).filter(models.Room.room_id == room_id).first()
    if not room or room.host_id != player_id:
        raise HTTPException(status_code=403, detail="Только хост может начать игру")

    participants = db.query(models.RoomParticipant).filter(models.RoomParticipant.room_id == room_id).all()
    if len(participants) < 2:
        raise HTTPException(status_code=400, detail="Нужно минимум 2 игрока")

    player_ids = [p.player_id for p in participants]
    users = db.query(models.User).filter(models.User.player_id.in_(player_ids)).all()
    names_list = [u.name for u in users]

    roles_distribution = imposter(db, names_list)
    if "error" in roles_distribution:
        raise HTTPException(status_code=500, detail=roles_distribution["error"])

    for p in participants:
        current_user = next(u for u in users if u.player_id == p.player_id)
        user_data = roles_distribution[current_user.name]
        p.role = "Imposter" if user_data["role"] == "Imposter" else user_data["card_name"]
    
    db.commit()
    await manager.broadcast_to_room(room_id, {"event": "game_started", "message": "Роли выданы"})
    
    return {"status": "game_started"}

@router.get("/get-my-role", response_model=PlayerRoleResponse) 
def get_my_role(room_id: str, player_id: str, db: Session = Depends(get_db)):
    participant = db.query(models.RoomParticipant).filter(
        models.RoomParticipant.room_id == room_id,
        models.RoomParticipant.player_id == player_id
    ).first()

    if not participant or not participant.role:
        return {"status": "waiting", "role": None}
    
    if participant.role == "Imposter":
        return {
            "status": "active", 
            "role": "Imposter", 
            "card_name": "ШПИОН"
        }
    card = db.query(models.Card).filter(models.Card.card_name == participant.role).first()
    return {
        "status": "active", 
        "role": "Player", 
        "card_name": card.card_name, 
        "image_url": card.image_url, 
        "elixir": card.elixir_cost
    }

@router.post("/game-reset", response_model=SimpleStatusResponse)
async def reset_game(room_id: str, player_id: str, db: Session = Depends(get_db)):
    room = db.query(models.Room).filter(models.Room.room_id == room_id).first()
    if not room or room.host_id != player_id:
        raise HTTPException(status_code=403, detail="Только хост может сбросить игру")
    
    db.query(models.RoomParticipant).filter(models.RoomParticipant.room_id == room_id).update({models.RoomParticipant.role: None})
    db.commit()

    await manager.broadcast_to_room(room_id, {"event": "game_reset"})
    return {"status": "reset_ok"}