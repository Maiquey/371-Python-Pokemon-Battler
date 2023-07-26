class Pokemon:
    def __init__(self, name, ability):
        self.hp = 100
        self.alive = True
        self.name = name
        self.ability = ability

    def attcked(self, damage):
        self.hp -= damage
