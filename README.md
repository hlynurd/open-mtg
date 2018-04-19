# OpenMTG

An experimental framework for writing, testing and evaluating agents for the card game Magic: The Gathering.

### Dependencies

* [Jupyter notebook](http://jupyter.org/) 
* [itertools](https://docs.python.org/3/library/itertools.html)
* [NumPy](http://www.numpy.org/)
* [math](https://docs.python.org/3/library/math.html)
* [random](https://docs.python.org/3/library/random.html)
* [copy](https://docs.python.org/3/library/copy.html)


## Authors

* **Hlynur Davíð Hlynsson** - *Initial work* - [hlynurd](https://github.com/hlynurd)


## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Usage

A game is initialized with two players, which are initialized with a python decklist of cards:

```python
from decklists import *
from game import *
game = Game(Player(get_8ed_core_gold_deck()), Player(get_8ed_core_silver_deck()))
game.start_game()
```

The state of the game determines which player is allowed to act. The game logic always assumes that the player with priority is the currently acting player. This holds even if the acting player does not have priority a strict sense, for example where blockers are declared. 

A simple game loop where two players perform random actions against each other: 

```python
while not game.is_over():
    legal_moves = game.get_moves()
    move = random.choice(legal_moves)
    game.make_move(move)
```

The list of legal moves returned by game depend on the state of the game. An action to pass priority is returned as the string "Pass" or an empty list. The most important one is which phase or step it is, accessed by:

```python
game.phases[game.current_phase_index]
```

Below, when we reference "player" it is always the acting player, kept in:

```python
game.player_with_priority
```


# Main phase

Game returns a list of performable actions by the player. This is a list of indexes of cards in hand that can be played: Lands if the player has not played a land yet, or spells if the player has mana in their mana pool to pay for it. The list also contains indexes of activatable abilities by permanents they control.

# Declare Attackers Step

