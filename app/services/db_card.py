from app.db.session import SessionLocal
import app.db.models as models
from app.db.cards_list import CARDS_LIST

def seed_cards():
    db = SessionLocal()
    
    for card_data in CARDS_LIST:
        exists = db.query(models.Card).filter(models.Card.card_name == card_data["name"]).first()
        
        if not exists:
            new_card = models.Card(
                card_name=card_data["name"],
                elixir_cost=card_data.get("elixir"),
                image_url=card_data["image_url"]
            )
            db.add(new_card)
    
    db.commit()
    db.close()
    print("Все карты из списка в базе")

if __name__ == "__main__":
    seed_cards()