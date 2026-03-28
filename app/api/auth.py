from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import uuid
import app.db.models as models
from app.db.session import get_db
from app.schemas.schemas import UserData, UserAuthResponse
from app.core.hasp import get_password_hash, verify_password

router = APIRouter()

@router.post("/player-reg", status_code=status.HTTP_201_CREATED, response_model=UserAuthResponse)
def registration(data: UserData, db: Session = Depends(get_db)):
    user_exists = db.query(models.User).filter(models.User.name == data.name).first()
    if user_exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Пользователь с таким именем уже существует."
        )

    new_player_id = str(uuid.uuid4())
    new_user = models.User(
        name=data.name, 
        password=get_password_hash(data.password),
        player_id=new_player_id
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "status": "registered", 
        "player_id": new_user.player_id,
        "username": new_user.name
    }

@router.post("/player-log", response_model=UserAuthResponse)
def login(data: UserData, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.name == data.name).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    
    if not verify_password(data.password, user.password):
        raise HTTPException(status_code=401, detail="Неверный пароль")
    
    return {
        "status": "logged", 
        "player_id": user.player_id,
        "username": user.name
    }