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
   Pokemon("Pikachu", {"Thunderbolt": 20, "Quick Attack": 15}, 25, 26, "Raichu"),
    Pokemon("Bulbasaur", {"Vine Whip": 18, "Solar Beam": 30}, 1, 3, "Venusaur"),
    Pokemon("Charmander", {"Ember": 17, "Scratch": 14}, 4, 6, "Charizard"),
    Pokemon("Squirtle", {"Water Gun": 19, "Bite": 16}, 7, 9, "Blastoise"),
    Pokemon("Jigglypuff", {"Sing": 10, "Rollout": 25}, 39, 40, "Wigglytuff"),
    Pokemon("Meowth", {"Scratch": 14, "Pay Day": 12}, 52, 53, "Persian"),
    Pokemon("Psyduck", {"Water Gun": 19, "Confusion": 21}, 54, 55, "Golduck"),
    Pokemon("Geodude", {"Rock Throw": 16, "Magnitude": 23}, 74, 76, "Golem"),
    Pokemon("Abra", {"Teleport": 10, "Psybeam": 20}, 63, 65, "Alakazam"),
    Pokemon("Eevee", {"Quick Attack": 15, "Bite": 16}, 133, 134, "Vaporeon"),
    Pokemon("Mewtwo", {"Psychic": 35, "Shadow Ball": 25}, 150, 151, "Mew"),
]

        