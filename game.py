import random as random
import numpy as np
from players import *
from itertools import chain, combinations

# TODO: Throw away "active_player_index", better to just call "active_player.index"
# TODO: throw away "abs(x-1)", "1-x" works as well to bitflip
class Game:
    def __init__(self, player0, player1):
        self.players = [player0, player1]
        player0.index = 0
        player1.index = 1
        self.starting_hand_size = 7
        self.attackers = []
        self.blockers = []
        self.battlefield = []
        self.phases = ["Main Phase", "Declare Attackers Step", "Declare Blockers Step", "509.2", "510.1c",
                       "Combat Damage Step", "Main Phase", "End Step"]
        self.current_phase_index = 0
        # two counters to help keep track of damage assignment - per attacker - per bocker, respectively
        self.attacker_counter = 0
        self.blocker_counter = 0
        
    def make_move(self, player, move):
        if self.phases[self.current_phase_index] == "Main Phase":
            playable_indices = player.get_playable_cards()
            callable_permanents, ability_indices = player.get_activated_abilities(self)
            number_of_legal_moves = len(playable_indices) + sum(ability_indices)        
            if move < len(playable_indices):
                player.play_card(playable_indices[move], self)
            elif move is not number_of_legal_moves:
                move -= len(playable_indices)
                for i in range(len(ability_indices)):
                    if move > ability_indices[i]:
                        move -= ability_indices[i]
                    else:
                        callable_permanents[i].use_tapped_ability(move-1)        
            else: # passing priority
                self.player_with_priority = self.active_player.get_opponent(self)
        if self.phases[self.current_phase_index] == "Declare Attackers Step":
            attacking_player = self.active_player
            attacking_player.has_attacked = True
            eligible_attackers = attacking_player.get_eligible_attackers(self)
            xs = list(range(len(eligible_attackers)))
            powerset = list(chain.from_iterable(combinations(xs,n) for n in range(len(xs)+1)))
            element = powerset[move]
            chosen_attackers = [eligible_attackers[i] for i in element]
            self.attackers = chosen_attackers
        if self.phases[self.current_phase_index] == "Declare Blockers Step":
            blocking_player = self.nonactive_player
            blocking_player.has_blocked = True
            eligible_blockers = blocking_player.get_eligible_blockers(self)
            if len(eligible_blockers) is 0:
                return -1
            all_blocking_assignments = list(range(np.power(len(self.attackers)+1, len(eligible_blockers))))            
            reshaped_assignments = np.reshape(all_blocking_assignments, ([len(self.attackers)+1] * len(eligible_blockers)))
            blocking_assignments = np.argwhere(reshaped_assignments==move)[0]
            for i in range(len(blocking_assignments)):                
                if blocking_assignments[i] != len(self.attackers):
                    self.attackers[blocking_assignments[i]].is_blocked_by.append(eligible_blockers[i])
                    eligible_blockers[i].is_blocking.append(self.attackers[blocking_assignments[i]])
                    self.blockers.append(eligible_blockers[i])            
        if self.phases[self.current_phase_index] == "509.2": 
            for i in range(len(self.attackers)):
                if len(self.attackers[i].is_blocked_by) is not 0:
                    if len(self.attackers[i].damage_assignment_order) is 0:
                        self.attackers[i].set_damage_assignment_order(move)
                        return 1
            return -1
        if self.phases[self.current_phase_index] == "510.1c": 
            all_done = False
            self.assign_damage_deterministically(player,
                                                self.attackers[self.attacker_counter], self.blocker_counter, move)
            self.blocker_counter += 1
            if self.blocker_counter >= len(self.attackers[self.attacker_counter].is_blocked_by):
                self.blocker_counter = 0
                self.attacker_counter += 1
            if self.attacker_counter >= len(self.attackers):
                all_done = True
            #return all_done

    def assign_damage_deterministically(self, player, attacker, index, amount):
        blocker_i = attacker.damage_assignment_order[index]
        remaining_health = blocker_i.toughness - blocker_i.damage_taken
        attacker.assign_damage(index, amount)
        return attacker.damage_to_assign > 0
            
    def go_to_next_phase(self):
        self.current_phase_index += 1
        self.player_with_priority = self.active_player
        if self.current_phase_index == len(self.phases):
            self.start_new_turn()
        if self.phases[self.current_phase_index] == "Combat Damage Step" :
            if self.apply_combat_damage():
                print("player 0 life %i player 1 life %i" %(self.players[0].life, self.players[1].life))
                self.check_state_based_actions()
                if self.is_over():
                    print("Game is over!")
                    if self.players[0].has_lost: self.players[1].wins += 1
                    else:               self.players[0].wins += 1
                    print("player 0 wins: %i, player 1 wins: %i" % (self.players[0].wins, self.players[1].wins))
            self.clean_up_after_combat()
               
    def get_legal_moves(self, player):
        if self.phases[self.current_phase_index] == "Main Phase":
            playable_indices = player.get_playable_cards()
            _, ability_indices = player.get_activated_abilities(self)
            return list(range(len(playable_indices) + sum(ability_indices) + 1))
        if self.phases[self.current_phase_index] == "Declare Attackers Step":
            attacking_player = self.active_player
            if attacking_player.has_attacked:
                return [-1]
            # next two lines get the power set of attackers
            eligible_attackers = attacking_player.get_eligible_attackers(self)
            xs = list(range(len(eligible_attackers)))            
            return list(range(len(list(chain.from_iterable(combinations(xs,n) for n in range(len(xs)+1))))))
        if self.phases[self.current_phase_index] == "Declare Blockers Step":
            blocking_player = self.nonactive_player
            if blocking_player.has_blocked:
                return [-1]
            eligible_blockers = blocking_player.get_eligible_blockers(self)
            return list(range(np.power(len(self.attackers)+1, len(eligible_blockers))))
        if self.phases[self.current_phase_index] == "509.2": 
            for i in range(len(self.attackers)):
                if len(self.attackers[i].is_blocked_by) is not 0:
                    if len(self.attackers[i].damage_assignment_order) is 0:
                        return list(range(math.factorial(len(self.attackers[i].is_blocked_by))))
            return [-1]
        if self.phases[self.current_phase_index] == "510.1c": 
            if len(self.attackers) is 0 or self.attacker_counter >= len(self.attackers):
                return [-1]
            return self.get_possible_damage_assignments(player, self.attackers[self.attacker_counter], self.blocker_counter)        
        if self.phases[self.current_phase_index] == "Combat Damage Step":  
            return [-1]
        if self.phases[self.current_phase_index] == "End Step":  
            return [-1]

            
    def get_possible_damage_assignments(self, player, attacker, index):
        if  len(attacker.damage_assignment_order) is 0:
            return [-1]
        blocker_i = attacker.damage_assignment_order[index]
        remaining_health = blocker_i.toughness - blocker_i.damage_taken
        if attacker.damage_to_assign < remaining_health or index == len(attacker.damage_assignment_order)-1:
            return list(range(attacker.damage_to_assign, attacker.damage_to_assign+1))
        else:
            return list(range(remaining_health, attacker.damage_to_assign+1))
        
            
    def start_game(self):
        self.active_player_index = random.randint(0, len(self.players)-1)                
        print("player %i goes first" % (self.active_player_index))
        self.nonactive_player = self.players[1-self.active_player_index]
        self.active_player = self.players[self.active_player_index]
        self.player_with_priority = self.active_player
        self.active_player.can_play_land = True
        for i in range(len(self.players)):
            self.players[i].shuffle_deck()
            for j in range(self.starting_hand_size):
                self.players[i].draw_card()     
    def start_new_turn(self):
        self.current_phase_index = 0
        self.active_player_index = (self.active_player_index + 1) % len(self.players)        
        self.active_player = self.players[self.active_player_index]        
        self.player_with_priority = self.active_player
        self.nonactive_player = self.players[1-self.active_player_index]
        self.active_player.draw_card()
        self.active_player.can_play_land = True
        for permanent in self.battlefield:
            permanent.is_tapped = False
            if isinstance(permanent, Creature):
                permanent.summoning_sick = False
                permanent.damage = 0
        for i in range(len(self.players)):
            self.players[i].reset_mp() 
            self.players[i].has_attacked = False 
            self.players[i].has_blocked = False
    def is_over(self):        
        for i in range(len(self.players)):
            if self.players[i].has_lost:
                return True
        return False
    def apply_combat_damage(self):
        any_attackers = False
        for permanent in self.battlefield:
            if isinstance(permanent, Creature):
                if permanent in self.attackers:
                    if len(permanent.is_blocked_by) > 0:
                        for i in range(len(permanent.is_blocked_by)):                        
                            permanent.is_blocked_by[i].take_damage(permanent.damage_assignment[i])
                            permanent.take_damage(permanent.is_blocked_by[i].power)
                    else:
                        permanent.deal_combat_damage_to_opponent(self)      
                any_attackers = True
        return any_attackers
    def check_state_based_actions(self):
        #704.5g
        for permanent in self.battlefield:
            if isinstance(permanent, Creature):
                if permanent.is_dead:
                    self.battlefield.remove(permanent)
                    permanent.owner.graveyard.append(permanent)
                    
    def clean_up_after_combat(self):
        # TODO: Simplify this and test!
        self.attackers = []
        self.blockers = []
        self.attacker_counter = 0
        self.blocker_counter = 0
        for permanent in self.battlefield:
            if isinstance(permanent, Creature):
                # TODO: attribute "is_attacking" seems to be useless, remove this from everywhere
                permanent.is_attacking = []
                permanent.is_blocking = []
                permanent.is_blocked_by = []
                permanent.damage_assignment_order = []
                permanent.damage_assignment = []