import math
import random as random


def perform_random_main_phase_action(player, game):
    passed = False
    playable_indices = player.get_playable_cards()
    callable_permanents, ability_indices = player.get_activated_abilities(game)
    action_count = len(ability_indices) + len(playable_indices)
    if action_count > 0:
        tap_chance = (len(ability_indices) / float(action_count))
    if random.random() < 0.01 or action_count == 0:
        passed = True
    elif random.random() > tap_chance:
        player.play_card(playable_indices[0], game)
        # pay randomly the generic mana cost of the card
        while player.generic_debt > 0:
            eligible_colors = player.get_nonempty_mana_colors()
            player.pay_generic_debt(eligible_colors[random.randint(0, len(eligible_colors) - 1)])
    else:
        callable_permanents[0].use_tapped_ability(0)
    return passed


def declare_random_attackers(player, game):
    eligible_attackers = player.get_eligible_attackers(game)
    attackers = []
    for creature in eligible_attackers:
        if random.random() < 0.5:
            creature.is_attacking.append(creature.owner.get_opponent(game))
            attackers.append(creature)
    return attackers


def declare_random_blockers(player, attackers, game):
    eligible_blockers = player.get_eligible_blockers(game)
    blockers = []
    for creature in eligible_blockers:
        if random.random() < 0.5:
            attacker_index = random.randint(0, len(attackers) - 1)
            blocked_attacker = attackers[attacker_index]
            creature.is_blocking.append(blocked_attacker)
            blocked_attacker.is_blocked_by.append(creature)
            blockers.append(creature)
    return blockers


def assign_random_damage_assignment_orders(player, attackers, game):
    for attacker in attackers:
        order = math.factorial(len(attacker.is_blocked_by))
        random_order = random.randint(0, order)
        attacker.set_damage_assignment_order(random_order - 1)


def assign_damage_randomly(player, attacker):
    for i in range(len(attacker.damage_assignment_order)):
        blocker_i = attacker.damage_assignment_order[i]
        remaining_health = blocker_i.toughness - blocker_i.damage_taken
        if attacker.damage_to_assign < remaining_health or i == len(attacker.damage_assignment_order) - 1:
            attacker.assign_damage(i, attacker.damage_to_assign)
            break
        else:
            random_damage = random.randint(remaining_health, attacker.damage_to_assign)
            attacker.assign_damage(i, random_damage)
            if attacker.damage_to_assign == 0:
                break

            # delete these functions!
