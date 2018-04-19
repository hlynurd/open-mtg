# OpenMTG
![OpenMTG logo](https://raw.githubusercontent.com/hlynurd/open-mtg/master/logo.png) 

An experimental framework for writing, testing and evaluating agents for the card game Magic: The Gathering.

### Dependencies

* [Jupyter notebook](http://jupyter.org/) 
* [itertools](https://docs.python.org/3/library/itertools.html)
* [NumPy](http://www.numpy.org/)
* [math](https://docs.python.org/3/library/math.html)
* [random](https://docs.python.org/3/library/random.html)
* [copy](https://docs.python.org/3/library/copy.html)


## Authors

* **Hlynur Davíð Hlynsson** - [hlynurd](https://github.com/hlynurd)

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Contributing

I have a keen in branching out this project, please send me an email so we can coordinate our collaboration efforts!

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

The list of legal moves returned by game depend on the state of the game. Currently this project supports lands and sorcery speed actions. An action to pass priority is returned as the string "Pass" or an empty list. The most important one is which phase or step it is, accessed by:

```python
game.phases[game.current_phase_index]
```

Below, when we reference "player" it is always the acting player, kept in:

```python
game.player_with_priority
```


### Main phase

Game returns a list of performable actions by the player. This is a list of indexes of cards in hand that can be played: Lands if the player has not played a land yet, or spells if the player has mana in their mana pool to pay for it. The list also contains indexes of activatable abilities by permanents they control.

### Declare Attackers Step

All combinations of eligible attackers are computed and indexed. Game returns a list of indices, and the combination that corresponds to this index is declared as attackers when the index is passed to make_move.

### Declare Blockers Step

This step is handled with the player taking decisions over several moves: Until each eligible blocker has been considered, the legal moves are the indices of the attackers or an additional index, corresponding to a "no block" choice.

### 509.2 "Damage Assignment Ordering"

This step is also handled in several moves: For each attacker, the player choose an index corresponding to an indexed list of permutations of blockers.

### 510.1c "Damage Assignment

Double loop of moves, until no more choices are necessary: For each creature, and for each blocker assigned to that creature (in the damage assignment order), the legal moves is the legal amount of damage to be assigned to that blocker by that creature.

### Corollary choices

For spells or abilities that require a target, the player must get an additional list of legal moves from the game to finish resolving that spell or ability. Paying for generic mana cost is also delayed, so the player must get a list of legal combinations to pay for generic mana and pay for it before passing priority. 
