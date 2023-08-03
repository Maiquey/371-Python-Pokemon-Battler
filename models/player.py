from models.pokemon import Pokemon
import copy

class Player:
    count = 0
    def __init__(self, sock):
        Player.count += 1
        self.clientId = Player.count
        self.ready = False
        self.sock = sock
        self.pokemons = []
        # Justin: Not sure if we need this? Since how would they capture it?
        # Originally thought they have access to all the pokemon
        # Unless you want to restrict how many pokemon they can choose from?
        self.capturePokemon(pokemonSeedData[Player.count % len(pokemonSeedData)])
        # Currently set to first pokemon in their list
        # TODO (If needed)
        # If we want them to choose their own pokemon then we have to change it
        self.battlePokemon = self.pokemons[0]
    
    def capturePokemon(self, pokemon):
        # deep_copy_pokemon = copy.deepcopy(pokemonSeedData[0])
        self.pokemons.append(copy.deepcopy(pokemon))

pokemonSeedData = [
    Pokemon("Pikachu", {"Thunderbolt": 20, "Quick Attack": 15}),
    Pokemon("Bulbasaur", {"Vine Whip": 18, "Razor Leaf": 22, "Solar Beam": 30}),
    Pokemon("Charmander", {"Ember": 17, "Scratch": 14}),
    Pokemon("Squirtle", {"Water Gun": 19, "Bite": 16}),
    Pokemon("Jigglypuff", {"Sing": 10, "Rollout": 25}),
    Pokemon("Meowth", {"Scratch": 14, "Pay Day": 12}),
    Pokemon("Psyduck", {"Water Gun": 19, "Confusion": 21}),
    Pokemon("Geodude", {"Rock Throw": 16, "Magnitude": 23}),
    Pokemon("Abra", {"Teleport": 10, "Psybeam": 20}),
    Pokemon("Eevee", {"Quick Attack": 15, "Bite": 16, "Swift": 18}),
]

        