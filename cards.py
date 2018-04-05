import itertools
class Card:
    def __init__(self):
        self.mc = {'White' : 0, 'Blue' : 0, 'Black' : 0, 'Red' : 0, 'Green' : 0, 'Colorless' : 0, 'Generic' : 0}
        self.tapped_abilities = []
    def play(self, owner, game):
        self.owner = owner
        self.is_tapped = False
        game.battlefield.append(self)
        
class Land(Card):
    def __init__(self, name, types, subtypes, tapped_abilities ):
        super(Land, self).__init__()
        self.types            = types
        self.subtypes         = subtypes
        self.tapped_abilities = tapped_abilities        
    def play(self, owner, game):
        super(Land, self).play(owner, game)
        self.owner.can_play_land = False
    def use_tapped_ability(self, index):
        if not self.is_tapped:
            self.is_tapped = True
            self.tapped_abilities[index](self)        
            
class Creature(Card):
    def __init__(self, name, subtypes, mc, power, toughness):
        super(Creature, self).__init__()
        self.name             = name
        self.mc               = {x: mc.get(x, 0) + self.mc.get(x, 0) for x in set(mc).union(self.mc)}
        self.base_power       = power
        self.power            = power
        self.base_toughness   = toughness        
        self.toughness        = toughness
        self.subtypes         = subtypes        
    def play(self, owner, game):
        super(Creature, self).play(owner, game)
        self.summoning_sick   = True
        self.is_dead          = False
        self.damage_taken     = 0
        self.damage_to_assign = 0        
        self.is_attacking     = []
        self.is_blocked_by    = []
        self.is_blocking      = []
        self.damage_assignment_order = []
        self.damage_assignment = []
    def take_damage(self, amount):
        self.damage_taken += amount
        if self.damage_taken >= self.toughness:
            self.is_dead = True
    def deal_combat_damage_to_opponent(self, game):
        game.players[1-self.owner.index].lose_life(self.power)
    def set_damage_assignment_order(self, order):
        all_permutations = list(itertools.permutations(self.is_blocked_by))
        self.damage_assignment_order = list(all_permutations[order]) 
        self.damage_to_assign = self.power
        self.damage_assignment = [0] * len(self.damage_assignment_order)
    def assign_damage(self, index, amount):
        self.damage_assignment[index] += amount
        self.damage_to_assign -= amount
        