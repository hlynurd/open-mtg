from game import *


class Node:
    """ A node in the game tree. Note wins is always from the viewpoint of playerJustMoved.
        Crashes if state not specified.
    """

    def __init__(self, move=None, parent=None, state=None):
        self.move = move  # the move that got us to this node - "None" for the root node
        self.parent = parent  # "None" for the root node
        self.child_nodes = []
        self.wins = 0
        self.visits = 0
        self.untried_moves = state.get_moves()  # future child nodes
        self.player_just_moved = state.player_just_moved  # the only part of the state that the Node needs later

    def uct_select_child(self):
        """ Use the UCB1 formula to select a child node. Often a constant UCTK is applied so we have
            lambda c: c.wins/c.visits + UCTK * sqrt(2*log(self.visits)/c.visits to vary the amount of
            exploration versus exploitation.
        """
        s = sorted(self.child_nodes, key=lambda c: c.wins / c.visits + np.sqrt(2 * np.log(self.visits) / c.visits))[-1]
        return s

    def add_child(self, m, s):
        """ Remove m from untriedMoves and add a new child node for this move.
            Return the added child node
        """
        n = Node(move=m, parent=self, state=s)
        self.untried_moves.remove(m)
        self.child_nodes.append(n)
        return n

    def update(self, result):
        """ Update this node - one additional visit and result additional wins.
        result must be from the viewpoint of playerJustmoved.
        """
        self.visits += 1
        self.wins += result

    def __repr__(self):
        return "[M:" + str(self.move) + " W/V:" + str(self.wins) + "/" + str(self.visits) + " U:" + str(
            self.untried_moves) + "]"


def uct(rootstate, itermax, verbose=False):
    """ Conduct a UCT search for itermax iterations starting from rootstate.
        Return the best move from the rootstate.
        Assumes 2 alternating players (player 1 starts), with game results in the range [0.0, 1.0]."""

    rootnode = Node(state=rootstate)

    for i in range(itermax):
        node = rootnode
        state = copy.deepcopy(rootstate)

        # mtg fix: shuffle own deck
        k = node.player_just_moved.index

        # the mcts rollouts don't randomize cards that have been seen with Index
        indexed_cards_in_deck = []
        # print("mcts print: %s" % (state.players))

        if len(state.players[k].deck) > 0:
            while len(state.players[k].deck) > 0 and state.players[k].deck[-1].deck_location_known:
                indexed_cards_in_deck.append(state.players[k].deck.pop())
        for indexed_card in indexed_cards_in_deck:
            state.players[k].deck.append(indexed_card)
        # and "imagine" a scenario for the opponent - this assumes knowledge of opponent decklist!

        state.players[k].shuffle_deck()
        opponent = state.players[1 - k]

        opponent_hand_size = len(opponent.hand)
        for j in range(opponent_hand_size):
            opponent.deck.append(opponent.hand.pop())

        opponent.shuffle_deck()

        for j in range(opponent_hand_size):
            opponent.draw_card()

        # Select
        while node.untried_moves == [] and node.child_nodes != []:  # node is fully expanded and non-terminal
            node = node.uct_select_child()
            state.make_move(node.move)

        # Expand
        if node.untried_moves != [] and node.parent == None:  # if we can expand (i.e. state/node is root)
            m = random.choice(node.untried_moves)
            state.make_move(m)
            node = node.add_child(m, state)  # add child and descend tree

        # Rollout - this can often be made orders of magnitude quicker using a state.GetRandomMove() function
        while not state.get_moves() == []:  # while state is non-terminal
            state.make_move(random.choice(state.get_moves()))

        # Backpropagate
        while node is not None:  # backpropagate from the expanded node and work back to the root node
            # state terminal. Update node with result from POV of node.playerJustMoved
            node.update(state.get_results(node.player_just_moved.index))
            node = node.parent
    return sorted(rootnode.child_nodes, key=lambda c: c.visits)[-1].move  # return the move that was most visited
