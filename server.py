import socket
import threading
import time
from models.player import Player

# dictionary of connected clients
# {client_id, Player}
clients = {}

# main server thread
def server_main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('localhost', 8080))
    server_socket.listen(2) # Set the backlog to 2 to allow two clients to connect.

    print("server listening on port 8080")

    # allow 2 clients to connect
    while True:
        try:
            client_socket, client_address = server_socket.accept()
            send_dictionary_length(client_socket, len(clients)) # Send the player count the the client


            if len(clients) < 2: # only two players are allowed to play
                print(f"Accepted connection from {client_address}")

                # create player entry in clients
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
            client.get_socket().send(message.encode("utf-8"))
        except:
            print("Error broadcasting message.")

# check if all players are ready before starting game
def ready_check():
    for player in clients.values():
        if not player.is_ready():
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
