class Player:
    def __init__(self, sock):
        self.hp = 100
        self.energy = 100
        self.alive = True
        self.ready = False
        self.sock = sock

    def get_hp(self):
        return self.hp

    def get_energy(self):
        return self.energy

    def is_alive(self):
        return self.alive

    def is_ready(self):
        return self.ready

    def get_socket(self):
        return self.sock