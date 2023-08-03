import socket
import threading
import time
import pickle
from models.player import Player

lock = threading.Lock()
clients_locked = False

# dictionary of connected clients
# {client_id, Player}
# Justin's Change: Changed Shotaro's conversion from list back to dictionary
clients = {}

# hard coded list of all implemented actions
actions = {}

# main server thread
def server_main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('localhost', 8080))
    server_socket.listen(2) # Set the backlog to 2 to allow two clients to connect.

    print("server listening on port 8080")

    # TODO
    # Still need to make sure there are 2 players are connected before starting - done
    # If theres only 1 player and they click "ready", game still starts - done

    # allow 2 clients to connect
    while True:
        try:
            client_socket, client_address = server_socket.accept()
            # Send the player count the the client for checking
            send_dictionary_length(client_socket, len(clients)) 


            if len(clients) < 2: # only two players are allowed to play
                print(f"Accepted connection from {client_address}")

                # create player entry in clients
                # Justin's Change: Changed Shotaro's conversion from list back to dictionary 
                p = Player(client_socket)
                clients[p.clientId] = p

                # serve client on seperate thread
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
            data = client_socket.recv(1024)
            if not data:
                break
            message = data.decode("utf-8")

            #split headers and payloads with :
            applicationMessage = message.split(":")

            # check headers and payloads
            msg_iterator = iter(applicationMessage)
            header = next(msg_iterator)

            # server request logic
            if header == "ready":
                msg = f"text:Player {client_id} is ready"
                broadcast_message(msg)
                clients[client_id].ready = True
                ready_check()
            elif header == "attack":
                attack_name = next(msg_iterator)
                if next(msg_iterator) == "damage":
                    damage = next(msg_iterator)
                    print(f"player {client_id} used {attack_name}, dealing {damage} damage!")
                    process_attack(client_id, attack_name, damage)
            elif header == "return":
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
    for client in clients.values():
        try:
            # Justin: Since we dont need to use getters/setters, replaced function called with class variable call
            if message == "game_start":
                # First send a message regarding the pokemon info         
                pokemonMsg = f"pokemon:{pickle.dumps(client.battlePokemon)}"
                client.sock.send(pokemonMsg.encode("utf-8"))
            client.sock.send(message.encode("utf-8"))
        except:
            print("Error broadcasting message.")

# check if all players are ready before starting game
def ready_check():
    # check if all players are ready
    for player in clients.values():
        # Justin: Since we dont need to use getters/setters, replaced function called with class variable call
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

def start_game():
    broadcast_message("text:All players are ready\nStarting Game\n3")
    time.sleep(1)
    broadcast_message("text:2")
    time.sleep(1)
    broadcast_message("text:1")
    time.sleep(1)
    broadcast_message("game_start")

def process_attack(client_id, attack_name, damage):
    global clients_locked

    opponent_id = 0

    # Should only ever be 2 clients at a time
    for key, value in clients.items():
        if key != client_id:
            opponent_id = key

    attacker = clients[client_id]
    opponent = clients[opponent_id]


    if clients_locked:
        attacker.sock.send("text:Waiting for other player to finish their turn".encode("utf-8"))
        return

    with lock:
        clients_locked = True
        broadcast_message("pause_counter")

        opponent.battlePokemon.get_attacked(int(damage))

        broadcast_message(f"log:player {client_id} used {attack_name}, dealing {damage} damage!")

        # calculate new hp vals
        attacker_hp = attacker.battlePokemon.current_hp
        opponent_hp = opponent.battlePokemon.current_hp

        time.sleep(1)
        try:
            # Send hp updates to clients
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
            attacker.sock.send("game_over:win".encode("utf-8"))
            opponent.sock.send("game_over:lose".encode("utf-8"))
        else:
            broadcast_message("resume_counter")

        clients_locked = False
        return

if __name__ == "__main__":
    server_main()

