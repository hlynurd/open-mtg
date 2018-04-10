import numpy as np
import random as random
from cards import *
import math
import copy

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
        self.passed_priority = True
        self.reset_mp()        
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
                new_game.make_move(new_game.players[self.index], legal_moves[i])
                move_values[i] = self.alphabeta(new_game, 5, -9999, 9999, new_game.player_with_priority.index is not self.index)
            print(move_values)
            
            winner = np.argwhere(move_values == np.amax(move_values))
            winner.flatten().tolist()
            arg = random.choice(winner)[0]
            return legal_moves[arg]
        
    # from wikipedia
    # this functions needs to be examined carefully, as the assumption from wikipedia does not hold: the players are not necessarily alternating their moves
    def alphabeta(self, new_game, depth, alpha, beta, maximizing_player):
        if depth == 0 or new_game.is_over():
            return new_game.players[self.index].heuristic_value(new_game)
        if maximizing_player:
            v = -9999
            for new_move in new_game.get_legal_moves(new_game.players[self.index]):
                another_new_game = copy.deepcopy(new_game)
                another_new_game.make_move(another_new_game.players[self.index], new_move)
                v = max(v, self.alphabeta(another_new_game, depth-1, alpha, beta, another_new_game.player_with_priority.index is not self.index))
                alpha = max(alpha, v)
                if beta <= alpha:
                    break
            return v
        else:
            v = 9999
            for new_move in new_game.get_legal_moves(new_game.players[1-self.index]):
                another_new_game = copy.deepcopy(new_game)
                another_new_game.make_move(another_new_game.players[1-self.index], new_move)
                v = min(v, self.alphabeta(another_new_game, depth-1, alpha, beta, another_new_game.player_with_priority.index is self.index))
                beta = min(beta, v)
                if beta <= alpha:
                    break
            return v
                        
                        
            
    def heuristic_value(self, game):
        if self.get_opponent(game).has_lost:
            return 9999
        if self.has_lost:
            return -9999
        enemy_bear_amount = 0
        own_bear_amount = 0
        own_power = 0
        enemy_power = 0
        own_toughness = 0
        enemy_toughness = 0
        for permanent in game.battlefield:
            if isinstance(permanent, Creature):
                if permanent.owner.index is self.index:
                    own_power += permanent.power
                    own_toughness += permanent.toughness
                    own_bear_amount += 1
                else:
                    enemy_power += permanent.power
                    enemy_toughness += permanent.toughness
                    enemy_bear_amount += 1
        value = (own_bear_amount - enemy_bear_amount) + (self.life - self.get_opponent(game).life) + (own_power - enemy_power) + (own_toughness - enemy_toughness)
        return value
                    
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
