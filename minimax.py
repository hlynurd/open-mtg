import random as random
import numpy as np
from players import *
from itertools import chain, combinations
from game import *
from cards import *
import copy
def heuristic_value(player, game):
    if player.get_opponent(game).has_lost:
        return 9999
    if player.has_lost:
        return -9999
    enemy_bear_amount = 0
    own_bear_amount = 0
    own_power = 0
    enemy_power = 0
    own_toughness = 0
    
    enemy_toughness = 0
    for permanent in game.battlefield:
        if isinstance(permanent, Creature):
            if permanent.owner.index is player.index:
                own_power += permanent.power
                own_toughness += permanent.toughness
                own_bear_amount += 1
            else:
                enemy_power += permanent.power
                enemy_toughness += permanent.toughness
                enemy_bear_amount += 1
    value = (own_bear_amount - enemy_bear_amount) + (player.life - player.get_opponent(game).life) + (own_power - enemy_power) + (own_toughness - enemy_toughness)
    return value
# from wikipedia
# not a good method for mtg, assumes full knowledge of both hands and deck orders
def alphabeta(player, game, depth, alpha, beta, maximizing_player):
    if depth == 0 or game.is_over():
        return heuristic_value(game.players[player.index], game)
    if maximizing_player:
        v = -9999
        for new_move in game.get_legal_moves(game.players[player.index]):
            game_copy = copy.deepcopy(game)
            game_copy.make_move(new_move)
            v = max(v, alphabeta(player, game_copy, depth-1, alpha, beta, game_copy.player_with_priority.index is not player.index))
            alpha = max(alpha, v)
            if beta <= alpha:
                break
        return v
    else:
        v = 9999
        for new_move in game.get_legal_moves(game.players[1-player.index]):
            game_copy = copy.deepcopy(game)
            game_copy.make_move(new_move)
            v = min(v, alphabeta(player, game_copy, depth-1, alpha, beta, game_copy.player_with_priority.index is player.index))
            beta = min(beta, v)
            if beta <= alpha:
                break
        return v         
