import numpy as np
import random as random
from cards import *
import math
import copy
import minimax
class Player:
    def __init__(self, deck):
        self.deck          = deck
        self.life          = 20        
        self.generic_debt  = 0
        self.can_play_land = False
        self.has_lost      = False                        
        self.hand          = []
        self.graveyard     = []
        self.has_attacked  = False
        self.has_blocked   = False
        self.passed_priority = True
        self.casting_spell = ""
        self.reset_mp()       
        
    def get_mp_as_list(self):
        mp_list = []
        for key in self.mp:
            for i in range(self.mp[key]):
                mp_list.append(key)
        return mp_list
        
    def take_damage(self, amount):
        self.lose_life(amount)
        
    def lose_life(self, amount):
        self.life -= amount
        if self.life < 1:
            self.has_lost = True
    def determine_move(self, method, game):
        legal_moves = game.get_legal_moves(self)
        if len(legal_moves) == 1:
            return legal_moves[0]
        if method == "random":
            return random.choice(legal_moves)
        if method == "alphabeta":
            move_values = [-9999] * len(legal_moves)
            for i in range(len(move_values)):
                new_game = copy.deepcopy(game)
                new_game.make_move(legal_moves[i])
                move_values[i] = minimax.alphabeta(self, new_game, 1, -9999, 9999, new_game.player_with_priority.index is not self.index)
            
            winner = np.argwhere(move_values == np.amax(move_values))
            winner.flatten().tolist()
            arg = random.choice(winner)[0]
            return legal_moves[arg]
                    
    def can_afford_card(self, card):
        for key in self.mp:
            if key != 'Generic':
                if self.mp[key] - card.mc[key] < 0:
                    return False
                elif sum(self.mp.values()) < sum(card.mc.values()):
                    return False
        return True
    
    def has_legal_targets(self, card, game):
        if card.name == "Vengeance" and len(game.get_tapped_creature_indices()) == 0:
            return False
        if card.name == "Stone Rain" and len(game.get_land_indices()) == 0:
            return False
        return True
    
    def get_opponent(self, game):
        return game.players[1-self.index]
    
    def get_playable_cards(self, game):
        playable_indices = []
        for i, card in enumerate(self.hand):
            #print(card.name)
            
            if isinstance(card, Land):
                if self.can_play_land:
                    playable_indices.append(i)
            elif isinstance(card, Creature):
                if self.can_afford_card(card):
                    playable_indices.append(i)
            elif isinstance(card, Sorcery):
                if self.can_afford_card(card) and self.has_legal_targets(card, game):
                    playable_indices.append(i)
            else:
                assert False
        return playable_indices
    
    def find_land_in_library(self, land_type):
        for i in range(len(self.deck)):
            if isinstance(self.deck[i], Land):
                 if land_type in self.deck[i].subtypes:
                        return i
        return -1

        
    
    def get_library_land_indices(self):
        land_indices = []
        for i in range(len(self.deck)):
            if isinstance(self.deck[i], Land):
                land_indices.append(i)
        return land_indices
    
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
        assert index in self.get_playable_cards(game)
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
                if isinstance(permanent, Creature) and not permanent.is_tapped and not permanent.cannot_block:
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
