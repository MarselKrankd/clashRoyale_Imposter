import random
from sqlalchemy.sql.expression import func
import app.db.models as models

def imposter(db, players):

    roles = {}

    random_card = db.query(models.Card).order_by(func.random()).first()
    
    if not random_card:
        return {"error": "База карт пуста!"}

    imposter_player = random.choice(players)
    
    for player in players:
        if player == imposter_player:
            roles[player] = {
                "role": "Imposter",
            }
        else:
            roles[player] = {
                "role": "Player",
                "card_name": random_card.card_name,
                "image_url": random_card.image_url,
                "elixir": random_card.elixir_cost
            }
            
    return roles

