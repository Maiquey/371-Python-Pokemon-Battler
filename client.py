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
                # TODO 
                # pass in information such as pokemon, own and opponent's hp vals, etc.

                # change pygame window to battle screen
                show_gameplay_screen()
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
TAN = (253, 222, 129)
MAGENTA = (186, 104, 200)
TEAL = (0, 128, 128)
ORANGE = (255,165,0)

window = pygame.display.set_mode(WINDOW_SIZE)
pygame.display.set_caption("Pokemon")
font = pygame.font.Font(None, 36)
underline_font = pygame.font.Font(None, 36)
underline_font.set_underline(True)
attack_log_font = pygame.font.Font(None, 28)
attack_log_font.set_underline(True)

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
    # Background
    window.fill(TAN)
    
    # Hud Window + Border
    hud_height = 200
    hud_window = pygame.Rect(0, (WINDOW_SIZE[1] - hud_height), WINDOW_SIZE[0], hud_height)
    pygame.draw.rect(window, WHITE, hud_window)

    hub_border_height = 5
    hud_border = pygame.Rect(0, (WINDOW_SIZE[1] - hud_height - hub_border_height), WINDOW_SIZE[0], hub_border_height)
    pygame.draw.rect(window, BLACK, hud_border)

    # Ability Buttons
    ability_height, ability_width = 60, 180
    padding = 20
    ability1_button = pygame.Rect(50, (WINDOW_SIZE[1] - ability_height - padding), ability_width, ability_height)
    pygame.draw.rect(window, MAGENTA, ability1_button, 0 , 3)
    border_button = pygame.Rect(48, (WINDOW_SIZE[1] - ability_height - padding), ability_width+4, ability_height)
    pygame.draw.rect(window, BLACK, border_button, 3 , 3)
    text_surface = font.render("Ability 1", True, WHITE)
    text_rect = text_surface.get_rect(center=ability1_button.center)
    window.blit(text_surface, text_rect)

    padding = 110
    ability2_button = pygame.Rect(50, (WINDOW_SIZE[1] - ability_height - padding), ability_width, ability_height)
    pygame.draw.rect(window, TEAL, ability2_button, 0 , 3)
    border_button = pygame.Rect(48, (WINDOW_SIZE[1] - ability_height - padding), ability_width+4, ability_height)
    pygame.draw.rect(window, BLACK, border_button, 3 , 3)
    text_surface = font.render("Ability 2", True, WHITE)
    text_rect = text_surface.get_rect(center=ability2_button.center)
    window.blit(text_surface, text_rect)

    # Health Bars
    # Player's Health
    pygame.draw.line(window, BLACK, (100, (WINDOW_SIZE[1] - hud_height - 80)), ((WINDOW_SIZE[0] - 300), (WINDOW_SIZE[1] - hud_height - 80)), 6)
    text_surface = underline_font.render("Player 1", True, BLACK)
    window.blit(text_surface, (100, (WINDOW_SIZE[1] - hud_height - 140)))
    p_health = 100
    text_surface = font.render("Health: " + str(p_health), True, BLACK)
    window.blit(text_surface, (100, (WINDOW_SIZE[1] - hud_height - 110)))
    # Enemy's Health
    pygame.draw.line(window, BLACK, (300, 100), ((WINDOW_SIZE[0] - 100), 100), 6)
    text_surface = underline_font.render("Player 2", True, BLACK)
    text_rect = text_surface.get_rect()
    text_rect.top, text_rect.right = 40, (WINDOW_SIZE[0] - 100)
    window.blit(text_surface,text_rect)
    p_health = 100
    text_surface = font.render("Health: " + str(p_health), True, BLACK)
    text_rect = text_surface.get_rect()
    text_rect.top, text_rect.right = 70, (WINDOW_SIZE[0] - 100)
    window.blit(text_surface, text_rect)

    # Attack History Window
    energy_box = pygame.Rect((WINDOW_SIZE[0] - 340), (WINDOW_SIZE[1] - 170), (WINDOW_SIZE[0] - (WINDOW_SIZE[0] - 270) + 20), 150)
    pygame.draw.rect(window, BLACK, energy_box, 3 , 3)
    text_surface = attack_log_font.render("Attack Log", True, BLACK)
    window.blit(text_surface, ((WINDOW_SIZE[0] - 340 + 5), (WINDOW_SIZE[1] - 170 + 5)))

    # Energy Counter
    box_size = 150
    energy_box = pygame.Rect(270, (WINDOW_SIZE[1] - box_size - 20), box_size, box_size)
    pygame.draw.rect(window, BLACK, energy_box, 3 , 3)
    text_surface = underline_font.render("Energy", True, ORANGE)
    box_center = energy_box.center
    text_rect = text_surface.get_rect(center=(box_center[0], box_center[1]-30))
    window.blit(text_surface, text_rect)
    # Timer (TEMPORARY)
    # TODO 
    # Will have to do something different like listen for events or something and move it somewhere else
    # Since this prevents other things from updating till this is finished
    clock = pygame.time.Clock()
    screen = pygame.display.get_surface()
    value = 0
    while value <= 100:
        # Create Value
        text_surface = font.render(str(value), True, ORANGE)
        box_center = energy_box.center
        text_rect = text_surface.get_rect(center=(box_center[0], box_center[1]+30))

        # Clear Old Value & Update
        screen.fill(WHITE, text_rect)
        window.blit(text_surface, text_rect)
        pygame.display.flip()
        value += 1
        clock.tick(5)

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