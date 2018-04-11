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

def get_8ed_core_silver_deck():
    decklist = []
    # TODO: add sorceries
    for i in range(8):
        decklist.append(Land    ("Plains", "Basic Land", "Plains", [lambda self: self.owner.add_mana({"White": 1})]))
    for i in range(7):
        decklist.append(Land    ("Island", "Basic Land", "Island", [lambda self: self.owner.add_mana({"Blue": 1})]))
    for i in range(4):
        decklist.append(Creature("Glory Seeker", "Human Soldier", {'White': 1, 'Generic' : 1}, 2, 2))
    for i in range(3):
        decklist.append(Creature("Giant Octopus", "Octopus", {'Blue': 1, 'Generic' : 3}, 3, 3))
    for i in range(2):
        decklist.append(Creature("Coral Eel", "Eel", {'Blue': 1, 'Generic' : 1}, 2, 1))
        decklist.append(Creature("Vizzerdrix", "Beast", {'Blue': 1, 'Generic' : 7}, 6, 6))
    for i in range(1):
        decklist.append(Creature("Eager Cadet", "Human Soldier", {'White': 1, 'Generic' : 0}, 1, 1))
        decklist.append(Creature("Fugitive Wizard", "Human Wizard", {'Blue': 1, 'Generic' : 0}, 1, 1))
    return decklist