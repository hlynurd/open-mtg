
# coding: utf-8

# In[1]:

import numpy as np
import random
import mcts
from cards import *
from players import *
from game import *    
from random_policy import *
from decklists import *


# In[2]:

#%%capture
player_0_wins = 0
player_1_wins = 0
for i in range(10):
    game = Game(Player(get_bear_wars_deck()), Player(get_bear_wars_deck()))
    game.start_game()
    while not game.is_over():
        #print("Current Game Phase: %s"  % (game.phases[game.current_phase_index]))
        if game.player_with_priority.index is 0:
            move = game.player_with_priority.determine_move(method="random", game=game)
        else:
            if True: #game.phases[game.current_phase_index] == "Declare Attackers Step":
                move = game.player_with_priority.determine_move(method="alphabeta", game=game)
#                if len(game.get_moves()) == 1:
#                    move = game.get_moves()[0]
#                else:
#                    move = mcts.uct(game, itermax = 100)
#                move = mcts.uct(game, itermax = 100)
            else:
                move = game.player_with_priority.determine_move(method="random", game=game)
        game.make_move(move)    
#        print("move: %i, current player's life: %i" % (move, game.player_with_priority.life))
    for j in range(2):
        print(game.get_legal_moves(game.players[j]))
    player_0_wins += game.players[0].wins
    player_1_wins += game.players[1].wins
    print("game is over! current standings: %i - %i" % (player_0_wins, player_1_wins))
print("player 0 wins: %i, player 1 wins: %i" % (player_0_wins, player_1_wins))


# In[3]:

print("player 0 wins: %i, player 1 wins: %i" % (player_0_wins, player_1_wins))

