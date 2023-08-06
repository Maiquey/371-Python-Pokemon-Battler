import socket
import threading
import time
import pickle
from models.player import Player

lock = threading.Lock()
clients_locked = False

# dictionary of connected clients
# {client_id, Player}
clients = {}

# main server thread
def server_main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('localhost', 8080))
    server_socket.listen(2) # Set the backlog to 2 to allow two clients to connect.

    print("server listening on port 8080")

    # allow clients to connect
    while True:
        try:
            # accept socket connection from client
            client_socket, client_address = server_socket.accept()
            # Send the player count the the client for checking
            send_dictionary_length(client_socket, len(clients)) 

            if len(clients) < 2: # only two players are allowed to play
                print(f"Accepted connection from {client_address}")

                # create player entry in clients
                # also store the player's socket connection inside this player object
                p = Player(client_socket)
                # store the client player object (and their socket connection) in the clients dictionary
                clients[p.clientId] = p

                # delegate further messaging between server and this client to a seperate thread
                client_thread = threading.Thread(target=communicate_with_client, args=(client_socket, p.clientId))
                client_thread.start()
        except Exception as e:
            print(f"Error accepting client connection: {e}")    
    
    # close server socket
    server_socket.close()
    
# client thread
def communicate_with_client(client_socket, client_id):
    while True:
        try:
            # receive msg from client
            data = client_socket.recv(1024)
            if not data:
                break
            message = data.decode("utf-8")
                
            # split headers and payloads with :
            applicationMessage = message.split(":")

            # iterate over headers and payloads using an iterator
            msg_iterator = iter(applicationMessage)
            header = next(msg_iterator)

            # server request logic
            # ready header signifying player is ready to start game
            if header == "ready":
                msg = f"ready_display:{client_id}:Player {client_id} READY" # changed header from text to ready_display, also pass the client id 
                broadcast_message(msg)
                pokemon_index = applicationMessage[1]
                clients[client_id].usePokemon(int(pokemon_index))
                clients[client_id].ready = True
                ready_check()
            # attack header that requests use of the 'attack' shared object
            elif header == "attack":
                attack_name = next(msg_iterator)
                if next(msg_iterator) == "damage":
                    damage = next(msg_iterator)
                    print(f"player {client_id} used {attack_name}, dealing {damage} damage!")
                    process_attack(client_id, attack_name, damage)
            # return header: signifies player has returned to lobby
            elif header == "return":
                # reset pokemon hp
                clients[client_id].battlePokemon.current_hp = clients[client_id].battlePokemon.hp 

        except Exception as e:
            print(f"Error handling client {client_id}: {e}")
            break

    # close connection
    print(f"Client {client_id} disconnected.")
    clients.pop(client_id)
    client_socket.close()

# send message to all connected clients
def broadcast_message(message):
    try:
        keys = list(clients.keys())
        if message == "game_start":
            # if player1 and player2 use same pokemon, player1 get Mewtwo as a special pokemon
            if clients[keys[0]].battlePokemon == clients[keys[1]].battlePokemon:
                clients[keys[0]].usePokemon(clients[keys[0]].pokemons[-1])
            pokemonMsg = pokemonMsg = f"pokemon:{pickle.dumps(clients[keys[0]].battlePokemon)}:{pickle.dumps(clients[keys[1]].battlePokemon)}"
            clients[keys[0]].sock.send(pokemonMsg.encode("utf-8"))
            pokemonMsg = pokemonMsg = f"pokemon:{pickle.dumps(clients[keys[1]].battlePokemon)}:{pickle.dumps(clients[keys[0]].battlePokemon)}"
            clients[keys[1]].sock.send(pokemonMsg.encode("utf-8"))
        clients[keys[0]].sock.send(message.encode("utf-8"))
        clients[keys[1]].sock.send(message.encode("utf-8"))
    except Exception as e:
        print("Error broadcasting message: ", {e})

# check if all players are ready before starting game
def ready_check():
    # check if all players are ready
    for player in clients.values():
        if not player.ready:
            return
    # check if there are only 2 players 
    if len(clients) == 2:
        start_game()

# send the dictionary length/player count to the client so it knows whether to draws a new pygame window or not
def send_dictionary_length(client_socket, length):
    try:
        message = f"dictionary_length:{length}"
        client_socket.send(message.encode("utf-8"))
    except Exception as e:
        print(f"Error sending dictionary length to client: {e}")   

# broadcast a countdown and game_start to all players
def start_game():
    broadcast_message("count_down:3")
    time.sleep(1)
    broadcast_message("count_down:2")
    time.sleep(1)
    broadcast_message("count_down:1")
    time.sleep(1)
    broadcast_message("count_down:GAME START")
    time.sleep(1)
    broadcast_message("game_start")

# SHARED OBJECT
# only one player may perform an attack at any time
# neither player can use abilities while an attack is occuring
# both players compete for use of this object in order to deal damage to their opponent
# we lock this process because it modifies the players' pokemon hp values, which is a critical section
# use a threading.lock() to ensure only one player can access the object at a time
def process_attack(client_id, attack_name, damage):
    global clients_locked

    opponent_id = 0

    # Should only ever be 2 clients at a time
    for key, value in clients.items():
        if key != client_id:
            opponent_id = key

    # keep track of who is attacking and who is the opponent
    attacker = clients[client_id]
    opponent = clients[opponent_id]

    # threading.lock() to ensure only one client is able to access the object at any time
    with lock:
        if clients_locked:
            return
        clients_locked = True

        # broadcast a lock message to all players to signify that shared object is in use
        broadcast_message("lock")

        # make damage calculations and update hp values
        opponent.battlePokemon.get_attacked(int(damage))

        # broadcast the successful attack as a log message to all clients
        broadcast_message(f"log:player {client_id} used {attack_name}, dealing {damage} damage!")

        # calculate new hp vals
        attacker_hp = attacker.battlePokemon.current_hp
        opponent_hp = opponent.battlePokemon.current_hp

        time.sleep(1)
        try:
            # Send hp updates to clients to update each player's UI
            attacker.sock.send(f"hp_update:{attacker_hp}:{opponent_hp}".encode("utf-8"))
            opponent.sock.send(f"hp_update:{opponent_hp}:{attacker_hp}".encode("utf-8"))
        except Exception as error:
            print(error)
        time.sleep(1)
        
        #check if game is over
        if opponent.battlePokemon.current_hp <= 0:
            print("game over!")
            # Reset each player's ready state for future games
            attacker.ready = False
            opponent.ready = False
            # Send gameover messages
            attacker.sock.send("game_over:win".encode("utf-8")) # attacker wins
            opponent.sock.send("game_over:lose".encode("utf-8")) # opponent loses
        else:
            # broadcast unlock message to signify the shared object is no longer in use
            broadcast_message("unlock")

        clients_locked = False
        return

if __name__ == "__main__":
    server_main()

