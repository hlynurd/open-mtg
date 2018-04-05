import random as random
from cards import *
import math

class Player:
    def __init__(self, deck):
        self.deck          = deck
        self.life          = 20        
        self.generic_debt  = 0
        self.can_play_land = False
        self.has_lost      = False                        
        self.hand          = []
        self.graveyard     = []
        self.wins          = 0
        self.has_attacked  = False
        self.has_blocked   = False
        self.reset_mp()        
    def lose_life(self, amount):
        self.life -= amount
        if self.life < 1:
            self.has_lost = True
            
    def can_afford_card(self, card):
        for key in self.mp:
            if key != 'Generic':
                if self.mp[key] - card.mc[key] < 0:
                    return False
                elif sum(self.mp.values()) < sum(card.mc.values()):
                    return False
        return True
    
    def get_opponent(self, game):
        return game.players[1-self.index]
    
    def get_playable_cards(self):
        playable_indices = []
        for i, card in enumerate(self.hand):
            if isinstance(card, Land):
                if self.can_play_land:
                    playable_indices.append(i)
            else:
                if self.can_afford_card(card):
                    playable_indices.append(i)
        return playable_indices
    def reset_mp(self):
        self.mp = {'White' : 0, 'Blue' : 0, 'Black' : 0, 'Red' : 0, 'Green' : 0, 'Colorless' : 0}
    
            
    def add_mana(self, mana):
        self.mp = {x: self.mp.get(x, 0) + mana.get(x, 0) for x in set(self.mp).union(mana)}
    def subtract_color_mana(self, mana):
        for key in self.mp:
            self.mp[key] -= mana[key]
        return mana['Generic']
    def shuffle_deck(self):
        random.shuffle(self.deck)
    def draw_card(self):
        if len(self.deck) < 1:
            self.has_lost = True
            return False
        drawn_card = self.deck.pop()
        self.hand.append(drawn_card)
        return drawn_card
    def play_card(self, index, game):
        assert index in self.get_playable_cards()
        card = self.hand.pop(index)
        self.generic_debt = self.subtract_color_mana(card.mc)
        card.play(self, game)
        return card
    def get_activated_abilities(self, game):
        callable_permanents = []
        number_of_abilities = []
        for permanent in game.battlefield:
            if permanent.owner.index is self.index:
                if len(permanent.tapped_abilities) > 0 and not permanent.is_tapped:
                    callable_permanents.append(permanent)
                    number_of_abilities.append(len(permanent.tapped_abilities))
        return callable_permanents, number_of_abilities
    def get_eligible_attackers(self, game):
        eligible_attackers = []
        for permanent in game.battlefield:
            if permanent.owner.index is self.index:
                if isinstance(permanent, Creature) and not permanent.is_tapped:
                    if not permanent.summoning_sick:
                        eligible_attackers.append(permanent)                    
        return eligible_attackers
    def get_eligible_blockers(self, game):
        eligible_blockers = []
        for permanent in game.battlefield:
            if permanent.owner.index is self.index:
                if isinstance(permanent, Creature) and not permanent.is_tapped:
                    eligible_blockers.append(permanent)                    
        return eligible_blockers
    def get_nonempty_mana_colors(self):
        mana_colors = []
        for key in self.mp:
            if key is not 'Generic':
                if self.mp[key] > 0:
                    mana_colors.append(key)
        return mana_colors
    def pay_generic_debt(self, color):
        self.mp[color]-= 1
        self.generic_debt -= 1
        return self.generic_debt
