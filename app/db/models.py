from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()
class User(Base):
    __tablename__ = "users" 
    id = Column(Integer, primary_key=True, index=True) 
    name = Column(String, unique=True, index=True)     
    password = Column(String)                          
    player_id = Column(String, unique=True)            
    current_room_id = Column(String, ForeignKey("rooms.room_id"), nullable=True)

class Card(Base):
    __tablename__ = "cards"
    id = Column(Integer, primary_key=True, index=True)
    card_name = Column(String, index=True)
    image_url = Column(String) 
    elixir_cost = Column(Integer, nullable=True) 

class Room(Base):
    __tablename__ = "rooms"
    id = Column(Integer, primary_key=True, index=True)
    room_id = Column(String, unique=True, index=True)
    room_pass = Column(String)
    host_id = Column(String) 

class RoomParticipant(Base):
    __tablename__ = "room_participants"
    id = Column(Integer, primary_key=True, index=True)
    room_id = Column(String, ForeignKey("rooms.room_id")) 
    player_id = Column(String, ForeignKey("users.player_id")) 
    role = Column(String, nullable=True) 