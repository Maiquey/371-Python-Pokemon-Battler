class Pokemon:
    def __init__(self, name, ability, number, boosted_number, boosted_name):
        self.hp = 100
        self.current_hp = 100
        self.name = name
        self.ability = ability
        self.number = number
        self.boosted_number = boosted_number
        self.boosted_name = boosted_name

    def get_attacked(self, damage):
        self.current_hp -= damage

