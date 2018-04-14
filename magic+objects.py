# coding: utf-8

# In[1]:

import mcts
from decklists import *
from game import *

# In[2]:

# todo: handle generic mana debt
# todo: implement 7th or 8th ed starter 2 player decks
# todo: clean up and sexify code
# %%capture
player_0_wins = 0
player_1_wins = 0
for i in range(20):
    game = Game(Player(get_8ed_core_gold_deck()), Player(get_8ed_core_silver_deck()))
    game.start_game()
    while not game.is_over():
        if game.player_with_priority.index is 0:
            move = game.player_with_priority.determine_move(method="random", game=game)
        else:
            #            move = game.player_with_priority.determine_move(method="random", game=game)
            if len(game.get_moves()) == 1:
                move = game.get_moves()[0]
            else:
                move = mcts.uct(game, itermax=25)
        game.make_move(move)
    if game.players[1].has_lost:
        player_0_wins += 1
    elif game.players[0].has_lost:
        player_1_wins += 1
    print("game is over! current standings: %i - %i" % (player_0_wins, player_1_wins))
print("player 0 wins: %i, player 1 wins: %i" % (player_0_wins, player_1_wins))
