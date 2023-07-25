import socket
import threading
import pygame

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
                show_gameplay_screen()
                # TODO 
                # pass in information such as pokemon, own and opponent's hp vals, etc.
                # change pygame window to battle screen
        except:
            break

# Setup pygame window
pygame.init()
WINDOW_SIZE = (800, 600)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
GREEN_LOCKED = (153, 255, 153)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)

window = pygame.display.set_mode(WINDOW_SIZE)
pygame.display.set_caption("Pokemon")
font = pygame.font.Font(None, 36)

def draw_button():
    button_rect = pygame.Rect(300, 270, 200, 60)
    pygame.draw.rect(window, GREEN, button_rect)
    text_surface = font.render("Ready", True, WHITE)
    text_rect = text_surface.get_rect(center=button_rect.center)
    window.blit(text_surface, text_rect)

def draw_button_lock():
    button_rect = pygame.Rect(300, 270, 200, 60)
    pygame.draw.rect(window, GREEN_LOCKED, button_rect)
    text_surface = font.render("Ready", True, WHITE)
    text_rect = text_surface.get_rect(center=button_rect.center)
    window.blit(text_surface, text_rect)
    pygame.display.flip()

def show_gameplay_screen():
    window.fill(BLUE)
    text_surface = font.render("GAMEPLAY", True, BLACK)
    text_rect = text_surface.get_rect(center=(WINDOW_SIZE[0] // 2, WINDOW_SIZE[1] // 2))
    window.blit(text_surface, text_rect)
    pygame.display.flip()

# Recive the player count from server
def receive_dictionary_length(client_socket):
    try:
        data = client_socket.recv(1024).decode("utf-8")
        if data.startswith("dictionary_length:"):
            length = int(data.split(":")[1])
            return length
        else:
            print("Invalid message received.")
    except Exception as e:
        print(f"Error receiving dictionary length: {e}")
    return None

if __name__ == "__main__":
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('localhost', 8080))

    # Check if there's already 2 players. If yes, close the connection. If no, continues 
    player_count = receive_dictionary_length(client_socket)
    if player_count >= 2:
        print(f"Sorry, the lobby is full")
        client_socket.close
    
    else:
        # Thread for incoming messages
        receiver_thread = threading.Thread(target=receive_message, args=(client_socket,))
        receiver_thread.start()

        # Pygame main loop
        running = True
        locked_in = False

        window.fill(WHITE)
        draw_button()
        pygame.display.flip()

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    if not locked_in:
                        button_rect = pygame.Rect(300, 270, 200, 60)
                        if button_rect.collidepoint(mouse_pos):
                            # lock the button and send ready message to server
                            locked_in = True
                            draw_button_lock()
                            ready_message = "ready"
                            client_socket.send(ready_message.encode("utf-8"))

        # Close the client socket and quit Pygame when the loop ends
        client_socket.close()
        pygame.quit()