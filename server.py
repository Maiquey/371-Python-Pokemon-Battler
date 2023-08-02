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
actions = {} #TODO: add actions

# main server thread
def server_main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('localhost', 8080))
    server_socket.listen(2) # Set the backlog to 2 to allow two clients to connect.

    print("server listening on port 8080")

    # TODO
    # Still need to make sure there are 2 players are connected before starting
    # If theres only 1 player and they click "ready", game still starts
    # allow 2 clients to connect
    while True:
        try:
            client_socket, client_address = server_socket.accept()
            send_dictionary_length(client_socket, len(clients)) # Send the player count the the client


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
            # TODO: add other options for headers for combat such as "attack"
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
    for player in clients.values():
        # Justin: Since we dont need to use getters/setters, replaced function called with class variable call
        if not player.ready:
            return
    start_game()

# send the dictionary length to the client so it knows whether to draws a new pygame window or not
def send_dictionary_length(client_socket, length):
    try:
        message = f"dictionary_length:{length}"
        client_socket.send(message.encode("utf-8"))
    except Exception as e:
        print(f"Error sending dictionary length to client: {e}")   

# TODO
# currently just simulates how a game may start
def start_game():
    broadcast_message("text:All players are ready\nStarting Game\n3")
    time.sleep(1)
    broadcast_message("text:2")
    time.sleep(1)
    broadcast_message("text:1")
    time.sleep(1)
    broadcast_message("game_start")

if __name__ == "__main__":
    server_main()

def process_attack(client_socket, client_id, attack):
    global clients_locked

    oponent = clients[(client_id + 1) % 2]

    request = client_socket.recv(1024).decode("utf-8")

    with lock:
        if clients_locked:
            client_socket.send("text:Waiting for other player to finish their turn".encode("utf-8"))
            return
    
        clients_locked = True
        client_socket.send("text:Executing attack".encode("utf-8"))

        target = clients[oponent]
        target.health -= attack.damage

        #send results
        client_socket.send(f"attack:{attack.name}:{attack.message}:{target.health}".encode("utf-8"))
        oponent.get_socket().send(f"attack:{attack.name}:{attack.message}:{target.health}".encode("utf-8"))
        
        #check if game is over
        if target.health <= 0:
            broadcast_message("game_over")
            clients[client_id].get_socket().send("text:You win!".encode("utf-8"))
            clients[oponent].get_socket().send("text:You lose!".encode("utf-8"))

        clients_locked = False
        return
