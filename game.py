import random as random
from players import *
class Game:
    def __init__(self, player0, player1):
        self.players = [player0, player1]
        player0.index = 0
        player1.index = 1
        self.starting_hand_size = 7
        self.battlefield = []
    def start_game(self):
        self.active_player_index = random.randint(0, len(self.players)-1)        
        print("player %i goes first" % (self.active_player_index))
        self.nonactive_player = self.players[abs(self.active_player_index-1)]
        self.active_player = self.players[self.active_player_index]
        self.active_player.can_play_land = True
        for i in range(len(self.players)):
            self.players[i].shuffle_deck()
            for j in range(self.starting_hand_size):
                self.players[i].draw_card()     
    def start_new_turn(self):
        self.active_player_index = (self.active_player_index + 1) % len(self.players)        
        self.active_player = self.players[self.active_player_index]        
        self.nonactive_player = self.players[abs(self.active_player_index-1)]
        self.active_player.draw_card()
        self.active_player.can_play_land = True
        for permanent in self.battlefield:
            permanent.is_tapped      = False
            if isinstance(permanent, Creature):
                permanent.summoning_sick = False
                permanent.damage = 0
        for i in range(len(self.players)):
            self.players[i].reset_mp() 
    def is_over(self):        
        for i in range(len(self.players)):
            if self.players[i].has_lost:
                return True
        return False
    def apply_combat_damage(self):
        for permanent in self.battlefield:
            if isinstance(permanent, Creature):
                if permanent.is_attacking:
                    for i in range(len(permanent.is_blocked_by)):
                        permanent.is_blocked_by[i].take_damage(permanent.damage_assignment[i])
                        permanent.take_damage(permanent.is_blocked_by[i].power)
    def check_state_based_actions(self):
        #704.5g
        for permanent in self.battlefield:
            if isinstance(permanent, Creature):
                if permanent.is_dead:
                    self.battlefield.remove(permanent)
                    permanent.owner.graveyard.append(permanent)
                    
    def clean_up_after_combat(self):
        for permanent in self.battlefield:
            if isinstance(permanent, Creature):
                permanent.is_attacking = []
                permanent.is_blocking = []
                permanent.is_blocked_by = []