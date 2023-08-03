class Pokemon:
    def __init__(self, name, ability, number):
        self.hp = 100
        self.current_hp = 100
        self.alive = True
        self.name = name
        self.ability = ability
        self.number = number

    def get_attacked(self, damage):
        self.current_hp -= damage

