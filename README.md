# OpenMTG

An experimental framework for writing, testing and evaluating agents for the card game Magic: The Gathering.

### Dependencies

* [Jupyter notebook](http://jupyter.org/) 
* [itertools](https://docs.python.org/3/library/itertools.html)
* [NumPy](http://www.numpy.org/)
* [math](https://docs.python.org/3/library/math.html)  
* [random](https://docs.python.org/3/library/random.html)  
* [copy] (https://docs.python.org/3/library/copy.html)


## Authors

* **Hlynur Davíð Hlynsson** - *Initial work* - [hlynurd](https://github.com/hlynurd)


## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Usage

A game is initialized with two players, which are initialized with a python decklist of cards:

```python
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
