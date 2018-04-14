from itertools import chain, combinations
import math
from players import *


class Game:
    def __init__(self, player0, player1):
        self.players = [player0, player1]
        player0.index = 0
        player1.index = 1
        self.starting_hand_size = 7
        self.attackers = []
        self.blockers = []
        self.battlefield = []
        self.stack_is_empty = True
        self.temporary_zone = []
        self.damage_targets = []
        self.active_player = self.players[random.randint(0, len(self.players) - 1)]
        self.nonactive_player = self.players[1 - self.active_player.index]
        self.player_just_moved = self.active_player
        self.player_with_priority = self.active_player
        # self.player_just_moved = {}
        self.phases = ["Main Phase", "Declare Attackers Step", "Declare Blockers Step", "509.2", "510.1c",
                       "Combat Damage Step", "Main Phase", "End Step"]
        self.current_phase_index = 0
        # two counters to help keep track of damage assignment - per attacker - per bocker, respectively
        self.attacker_counter = 0
        self.blocker_counter = 0

    def update_damage_targets(self):
        self.damage_targets = []
        self.damage_targets = self.get_battlefield_creatures() + self.players

    def get_moves(self):
        player = self.player_with_priority
        return self.get_legal_moves(player)

    def get_results(self, player_index):
        player = self.players[player_index]
        opponent = self.players[1 - player.index]
        assert self.is_over()
        if player.has_lost and opponent.has_lost:
            return 0.5
        if player.has_lost:
            return 0.0
        if opponent.has_lost:
            return 1.0

    def make_move(self, move, verbose=False):
        player = self.player_with_priority
        self.player_just_moved = player
        # TODO make the players pay up the generic mana cost debt if they have some!
        if player.generic_debt > 0:
            for mana in move:
                player.mp[mana] -= 1
                player.generic_debt -= 1
            return True
        if player.casting_spell != "":
            if player.casting_spell == "Vengeance":
                dead_creature = self.battlefield[move]
                self.battlefield.remove(dead_creature)
                dead_creature.owner.graveyard.append(dead_creature)
            if player.casting_spell == "Stone Rain":
                destroyed_land = self.battlefield[move]
                self.battlefield.remove(destroyed_land)
                destroyed_land.owner.graveyard.append(destroyed_land)
            if player.casting_spell == "Index":
                for i in range(len(move)):
                    indexed_card = player.deck.pop()
                    indexed_card.deck_location_known = True
                    self.temporary_zone.append(indexed_card)
                # TODO: Consider if the logic behind declaring blockers, declaring attackers and assigning combat damage
                #       can be simplified in a similar manner by allowing moves to be a list of lists
                for index in move:
                    player.deck.append(self.temporary_zone[index])
                self.temporary_zone = []
            if player.casting_spell == "Lava Axe":
                self.players[move].life -= 5
            if player.casting_spell == "Rampant Growth":
                if not move == "Refuse":
                    land_index = player.find_land_in_library(move)
                    land = player.deck.pop(land_index)
                    self.battlefield.append(land)
                    land.is_tapped = False
                    land.owner = player
                player.shuffle_deck()
            if player.casting_spell == "Volcanic Hammer":
                self.update_damage_targets()
                self.damage_targets[move].take_damage(3)
            player.casting_spell = ""
            return True

        # temp debugging:
        assert isinstance(move, int)

        # XXX: Rename -1 to "pass" in all files
        if move is -1:
            player.passed_priority = True
            self.player_with_priority = self.active_player.get_opponent(self)
            if self.players[0].passed_priority and self.players[1].passed_priority and self.stack_is_empty:
                self.go_to_next_phase()
            return True
        if self.phases[self.current_phase_index] == "Main Phase":
            playable_indices = player.get_playable_cards(self)
            callable_permanents, ability_indices = player.get_activated_abilities(self)
            if move < len(playable_indices):
                player.play_card(playable_indices[move], self)
            else:
                move -= len(playable_indices)
                for i in range(len(ability_indices)):
                    if move > ability_indices[i]:
                        move -= ability_indices[i]
                    else:
                        callable_permanents[i].use_tapped_ability(move - 1)

        if self.phases[self.current_phase_index] == "Declare Attackers Step":
            attacking_player = self.active_player
            attacking_player.has_attacked = True
            eligible_attackers = attacking_player.get_eligible_attackers(self)
            xs = list(range(len(eligible_attackers)))
            powerset = list(chain.from_iterable(combinations(xs, n) for n in range(len(xs) + 1)))
            element = powerset[move]
            chosen_attackers = [eligible_attackers[i] for i in element]
            self.attackers = chosen_attackers
            for attacker in self.attackers:
                attacker.is_tapped = True
        if self.phases[self.current_phase_index] == "Declare Blockers Step":
            blocking_player = self.nonactive_player
            blocking_player.has_blocked = True
            eligible_blockers = blocking_player.get_eligible_blockers(self)
            if len(eligible_blockers) is 0:
                return -1
            all_blocking_assignments = list(range(np.power(len(self.attackers) + 1, len(eligible_blockers))))
            reshaped_assignments = np.reshape(all_blocking_assignments,
                                              ([len(self.attackers) + 1] * len(eligible_blockers)))
            blocking_assignments = np.argwhere(reshaped_assignments == move)[0]
            for i in range(len(blocking_assignments)):
                if blocking_assignments[i] != len(self.attackers):
                    self.attackers[blocking_assignments[i]].is_blocked_by.append(eligible_blockers[i])
                    eligible_blockers[i].is_blocking.append(self.attackers[blocking_assignments[i]])
                    self.blockers.append(eligible_blockers[i])
        # for each attacker that’s become blocked, the active player announces the damage assignment order
        if self.phases[self.current_phase_index] == "509.2":
            for i in range(len(self.attackers)):
                if len(self.attackers[i].is_blocked_by) is not 0:
                    if len(self.attackers[i].damage_assignment_order) is 0:
                        self.attackers[i].set_damage_assignment_order(move)
                        return 1
            return -1
        # A blocked creature assigns its combat damage to the creatures blocking it
        if self.phases[self.current_phase_index] == "510.1c":
            self.assign_damage_deterministically(player,
                                                 self.attackers[self.attacker_counter], self.blocker_counter, move)
            self.blocker_counter += 1
            if self.blocker_counter >= len(self.attackers[self.attacker_counter].is_blocked_by):
                self.blocker_counter = 0
                self.attacker_counter += 1
            # return all_done

    def assign_damage_deterministically(self, player, attacker, index, amount):
        attacker.assign_damage(index, amount)
        return attacker.damage_to_assign > 0

    # NOTE: this function might be too specialized when more spells than 8ed have been added

    def get_tapped_creature_indices(self):
        tapped_creature_indices = []
        for i in range(len(self.battlefield)):
            if isinstance(self.battlefield[i], Creature):
                if self.battlefield[i].is_tapped:
                    tapped_creature_indices.append(i)
        return tapped_creature_indices

    def get_land_indices(self):
        land_indices = []
        for i in range(len(self.battlefield)):
            if isinstance(self.battlefield[i], Land):
                land_indices.append(i)
        return land_indices

    def get_battlefield_creatures(self):
        creatures = []
        for i in range(len(self.battlefield)):
            if isinstance(self.battlefield[i], Creature):
                creatures.append(self.battlefield[i])
        return creatures

    # NOTE: this function might have become too crowded, consider refactoring
    def get_legal_moves(self, player):
        if self.is_over():
            return []
        if player.generic_debt > 0:
            mp_as_list = player.get_mp_as_list()
            return list(itertools.combinations(mp_as_list, player.generic_debt))
        if player.casting_spell != "":
            # print("Returning a spell move now")
            if player.casting_spell == "Vengeance":
                return self.get_tapped_creature_indices()
            if player.casting_spell == "Stone Rain":
                return self.get_land_indices()
            if player.casting_spell == "Index":
                return list(itertools.permutations(list(range(min(5, len(player.deck))))))
            if player.casting_spell == "Lava Axe":
                return [0, 1]
            if player.casting_spell == "Volcanic Hammer":
                self.update_damage_targets()
                return list(range(len(self.damage_targets)))
            if player.casting_spell == "Rampant Growth":
                choices = ["Refuse"]
                basic_land_types = ["Plains", "Island", "Swamp", "Mountain", "Forest"]
                for land_type in basic_land_types:
                    if player.find_land_in_library(land_type) >= 0:
                        choices.append(land_type)
                return choices
            return [-1]
        if self.phases[self.current_phase_index] == "Main Phase":
            playable_indices = player.get_playable_cards(self)
            _, ability_indices = player.get_activated_abilities(self)
            non_passing_moves = list(range(len(playable_indices) + sum(ability_indices)))
            non_passing_moves.append(-1)
            return non_passing_moves  # append the 'pass' move action and return
        if self.phases[self.current_phase_index] == "Declare Attackers Step":
            attacking_player = self.active_player
            if attacking_player.has_attacked or player is not attacking_player:
                return [-1]
            # next two lines get the power set of attackers
            eligible_attackers = attacking_player.get_eligible_attackers(self)
            xs = list(range(len(eligible_attackers)))
            return list(range(len(list(chain.from_iterable(combinations(xs, n) for n in range(len(xs) + 1))))))
        if self.phases[self.current_phase_index] == "Declare Blockers Step":
            blocking_player = self.nonactive_player
            if blocking_player.has_blocked or player is not blocking_player:
                return [-1]
            eligible_blockers = blocking_player.get_eligible_blockers(self)
            return list(range(np.power(len(self.attackers) + 1, len(eligible_blockers))))
        # for each attacker that’s become blocked, the active player announces the damage assignment order
        if self.phases[self.current_phase_index] == "509.2":
            for i in range(len(self.attackers)):
                if len(self.attackers[i].is_blocked_by) is not 0:
                    if len(self.attackers[i].damage_assignment_order) is 0:
                        return list(range(math.factorial(len(self.attackers[i].is_blocked_by))))
            return [-1]

        if self.phases[self.current_phase_index] == "510.1c":
            if len(self.attackers) is 0 or self.attacker_counter >= len(self.attackers):
                return [-1]
            return self.get_possible_damage_assignments(player, self.attackers[self.attacker_counter],
                                                        self.blocker_counter)
        if self.phases[self.current_phase_index] == "Combat Damage Step":
            return [-1]
        if self.phases[self.current_phase_index] == "End Step":
            return [-1]

    @staticmethod
    def get_possible_damage_assignments(player, attacker, index):
        if len(attacker.damage_assignment_order) is 0:
            return [-1]
        blocker_i = attacker.damage_assignment_order[index]
        remaining_health = blocker_i.toughness - blocker_i.damage_taken
        if attacker.damage_to_assign < remaining_health or index == len(attacker.damage_assignment_order) - 1:
            return list(range(attacker.damage_to_assign, attacker.damage_to_assign + 1))
        else:
            return list(range(remaining_health, attacker.damage_to_assign + 1))

    def start_game(self):
        self.active_player.passed_priority = False
        self.active_player.can_play_land = True
        for i in range(len(self.players)):
            self.players[i].shuffle_deck()
            for j in range(self.starting_hand_size):
                self.players[i].draw_card()

    def start_new_turn(self):
        self.current_phase_index = 0
        self.active_player = self.players[1 - self.active_player.index]
        self.player_with_priority = self.active_player
        self.nonactive_player = self.players[1 - self.active_player.index]
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

    def go_to_next_phase(self):
        self.current_phase_index += 1

        if self.current_phase_index == len(self.phases):
            self.start_new_turn()
            return True
        if self.phases[self.current_phase_index] == "Combat Damage Step":
            if self.apply_combat_damage():
                self.check_state_based_actions()
            self.clean_up_after_combat()
        if self.phases[self.current_phase_index] == "Declare Blockers Step":
            self.nonactive_player.has_passed = False
            self.active_player.has_passed = True
            self.player_with_priority = self.nonactive_player
        else:
            self.nonactive_player.has_passed = True
            self.active_player.has_passed = False
            self.player_with_priority = self.active_player

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
        # 704.5g
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
