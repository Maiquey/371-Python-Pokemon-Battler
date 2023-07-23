import socket
import threading
import time
from player import Player

# dictionary of connected clients
# {client_id, Player}
clients = {}

# main server thread
def server_main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('localhost', 8080))
    server_socket.listen(2)

    print("server listening on port 8080")

    # allow 2 clients to connect
    while len(clients) < 2:
        try:
            client_socket, client_address = server_socket.accept()
            print(f"Accepted connection from {client_address}")

            # set a client ID
            client_id = len(clients) + 1

            # create player entry in clients
            clients[client_id] = Player(client_socket)

            # serve client on seperate thread
            client_thread = threading.Thread(target=communicate_with_client, args=(client_socket, client_id))
            client_thread.start()
        except Exception as e:
            print(f"Error accepting client connection: {e}")    
    
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

# TODO
# currently just simulates how a game may start
def start_game():
    broadcast_message("text:All players are ready\nStarting Game\n3")
    time.sleep(1)
    broadcast_message("text:2")
    time.sleep(1)
    broadcast_message("text:1")
    broadcast_message("game_start")

if __name__ == "__main__":
    server_main()
