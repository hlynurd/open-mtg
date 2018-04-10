from cards import *

def get_bear_wars_deck():
    decklist = []
    for i in range(12):
        decklist.append(Creature("Grizzly Bears 1", "bear", {'Green': 3, 'Generic' : 0}, 3, 1))
        decklist.append(Creature("Grizzly Bears 2", "bear", {'Green': 3, 'Generic' : 0}, 4, 1))
        decklist.append(Creature("Grizzly Bears 3", "bear", {'Green': 3, 'Generic' : 0}, 5, 1))
        decklist.append(Creature("Grizzly Bears 4", "bear", {'Green': 3, 'Generic' : 0}, 6, 1))
        decklist.append(Creature("Grizzly Bears 5", "bear", {'Green': 3, 'Generic' : 0}, 7, 1))
        decklist.append(Land    ("Forest", "Basic Land", "Forest", [lambda self: self.owner.add_mana({"Green": 1})]))
        decklist.append(Land    ("Taiga", "Land", "Mountain Forest", [lambda self: self.owner.add_mana({"Green": 1}),
                                                                             lambda self: self.owner.add_mana({"Red": 1})]))
    return decklist
