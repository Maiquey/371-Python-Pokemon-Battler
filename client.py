import socket
import threading

# incoming messages
def receive_message(sock):
    while True:
        try:
            data = sock.recv(1024)
            if not data:
                break
            
            # receive and split incoming message
            message = data.decode("utf-8").split(":")

            # iterate through headers and payloads
            msg_iterator = iter(message)
            header = next(msg_iterator)

            # text header for printing text
            if header == "text":
                print(next(msg_iterator))
            # game_start header for starting the game
            elif header == "game_start":
                print("loading game")
                # TODO 
                # pass in information such as pokemon, own and opponent's hp vals, etc.
                # change pygame window to battle screen
        except:
            break

# outgoing messages
# TODO
# change to not be based on user input, but send hard-coded strings based on button press inputs
def send_message(sock):
    while True:
        message = input()
        sock.send(message.encode("utf-8"))

if __name__ == "__main__":
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('localhost', 8080))
    
    # thread for incoming messages
    receiver_thread = threading.Thread(target=receive_message, args=(client_socket,))
    receiver_thread.start()
    
    # thread for outgoing messages
    sender_thread = threading.Thread(target=send_message, args=(client_socket,))
    sender_thread.start()