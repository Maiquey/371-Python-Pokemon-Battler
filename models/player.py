from models.pokemon import Pokemon

class Player:
    count = 0
    def __init__(self, sock):
        Player.count += 1
        self.clientId = Player.count
        self.ready = False
        self.sock = sock
        self.pokemons = pokemonSeedData
        self.battlePokemon = None
    
    def usePokemon(self, index):
        self.battlePokemon = self.pokemons[index]

pokemonSeedData = [
    Pokemon("Pikachu", {"Thunderbolt": 20, "Quick Attack": 15}, 25),
    Pokemon("Bulbasaur", {"Vine Whip": 18, "Solar Beam": 30}, 1),
    Pokemon("Charmander", {"Ember": 17, "Scratch": 14}, 4),
    Pokemon("Squirtle", {"Water Gun": 19, "Bite": 16}, 7),
    Pokemon("Jigglypuff", {"Sing": 10, "Rollout": 25}, 39),
    Pokemon("Meowth", {"Scratch": 14, "Pay Day": 12}, 52),
    Pokemon("Psyduck", {"Water Gun": 19, "Confusion": 21}, 54),
    Pokemon("Geodude", {"Rock Throw": 16, "Magnitude": 23}, 74),
    Pokemon("Abra", {"Teleport": 10, "Psybeam": 20}, 63),
    Pokemon("Eevee", {"Quick Attack": 15, "Bite": 16 }, 133),
    Pokemon("Mewtwo", {"Psychic": 35, "Shadow Ball": 25}, 150),
]

        