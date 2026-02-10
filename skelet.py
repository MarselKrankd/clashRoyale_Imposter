import random
cards=['принц',"рыцарь","меганайт","миньоны","шахтер",
       "армия скелетов","Ведьма","дровосек", "темная ночь", "колдун", "зап"]

def imposter(players):
    role={}
    loser=random.choice(players)
    card=random.choice(cards)
    for player in players:
        if player==loser:
            role[player]="Imposter)"
        else:
            role[player]=card
    print(role)

imposter(('rob','hog', 'ebenya'))



