import socket
import threading
import pygame
import pickle
from models.pokemon import Pokemon

# Global Varaibles
battle_pokemon = Pokemon("", {})
ability_lock = {}
current_energy = 0
energy_locked = False
game_over = False
player_hp = 100
enemy_hp = 100
global_threads = []

# incoming messages
def receive_message(sock):
    message_lock = threading.Lock()
    while True:
        try:
        # with message_lock:
            global energy_locked
            global player_hp
            global enemy_hp

            data = sock.recv(4096)
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
            elif header == "log":
                print(f"Log: {next(msg_iterator)}")
                # TODO: show these messages in the attack log instead of printing to console
            # game_start header for starting the game
            elif header == "pokemon":
                global battle_pokemon 
                battle_pokemon = pickle.loads(eval(next(msg_iterator)))
            elif header == "game_start":
                print("loading game")
                show_gameplay_screen()
            # energy locking while attack occurring
            # TODO: disable inputs while energy_locked OR implement energy refund message from server
            elif header == "pause_counter":
                energy_locked = True
            elif header == "resume_counter":
                energy_locked = False
            elif header == "hp_update":
                player_hp = int(next(msg_iterator))
                enemy_hp = int(next(msg_iterator))
                show_gameplay_screen()
            elif header == "game_over":
                print("game_over received")
                win_state = next(msg_iterator)
                render_game_over_screen(win_state)             

        except Exception as error:
            print(error)
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
ORANGE = (255, 165, 0)
GREY = (128, 128, 128)

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

def draw_return_button():
    button_rect = pygame.Rect(300, 270, 200, 60)
    pygame.draw.rect(window, WHITE, button_rect)
    text_surface = font.render("Return to Lobby", True, BLACK)
    text_rect = text_surface.get_rect(center=button_rect.center)
    window.blit(text_surface, text_rect)

# Function to draw ability buttons for battle view
def draw_ability_button(padding, name, colour):
    # Update Ability lock to be False, so its not greyed out and clickable
    global ability_lock
    ability_lock[name] = False

    # Draws ability buttons
    ability_height, ability_width = 60, 180
    ability1_button = pygame.Rect(50, (WINDOW_SIZE[1] - ability_height - padding), ability_width, ability_height)
    pygame.draw.rect(window, colour, ability1_button, 0 , 3)
    border_button = pygame.Rect(48, (WINDOW_SIZE[1] - ability_height - padding), ability_width+4, ability_height)
    pygame.draw.rect(window, BLACK, border_button, 3 , 3)
    text_surface = font.render(name, True, WHITE)
    text_rect = text_surface.get_rect(center=ability1_button.center)
    window.blit(text_surface, text_rect)

# Function to draw greyed out ability buttons for battle view
def draw_ability_button_lock(padding, name):
    # Update Ability lock to be True, so its  greyed out and unclickable
    global ability_lock
    ability_lock[name] = True

    # Draws greyed out ability buttons
    ability_height, ability_width = 60, 180
    ability1_button = pygame.Rect(50, (WINDOW_SIZE[1] - ability_height - padding), ability_width, ability_height)
    pygame.draw.rect(window, GREY, ability1_button, 0 , 3)
    border_button = pygame.Rect(48, (WINDOW_SIZE[1] - ability_height - padding), ability_width+4, ability_height)
    pygame.draw.rect(window, BLACK, border_button, 3 , 3)
    text_surface = font.render(name, True, WHITE)
    text_rect = text_surface.get_rect(center=ability1_button.center)
    window.blit(text_surface, text_rect)

# Function to draw energy counter section in battle view
def energy_counter():
    # List of ability dmgs/costs
    ability_dmg = list(battle_pokemon.ability.values())

    # Clock is used for incrementing and displaying on battle view
    clock = pygame.time.Clock()
    screen = pygame.display.get_surface()

    global current_energy
    global game_over
    global energy_locked

    # Energy Counter box location
    box_size = 150
    energy_box = pygame.Rect(270, (WINDOW_SIZE[1] - box_size - 20), box_size, box_size)

    # Incrementing Energy Counter
    while True:
        if game_over:
            break
        # Create Value
        text_surface = font.render(str(current_energy), True, ORANGE)
        box_center = energy_box.center
        text_rect = text_surface.get_rect(center=(box_center[0], box_center[1]+30))

        # Clear Old Value & Update
        white_rect = pygame.Rect(326, 523, 45, 24)
        screen.fill(WHITE, white_rect)
        window.blit(text_surface, text_rect)
        pygame.display.flip()

        # # For Testing Only (Ensuring game over logic works before server messaging implemented)
        # if current_energy == 20:
        #     render_game_over_screen("win")
        
        # Cap energy at 200
        if not energy_locked and current_energy < 200:
            current_energy += 1
        clock.tick(5)

        # Change Ability Button Colours from Greyed
        if current_energy >= ability_dmg[0]:
            draw_ability_button(20, list(battle_pokemon.ability.keys())[0], MAGENTA)
        if current_energy >= ability_dmg[1]:
            draw_ability_button(110, list(battle_pokemon.ability.keys())[1], TEAL)
        
def render_game_over_screen(win_state):
    global game_over
    window.fill(BLUE)
    font = pygame.font.Font(None, 72)
    if win_state == "win":
        gameover_text = "Game Won!"
    else:
        gameover_text = "Game Lost!"
    text_surface = font.render(gameover_text, True, BLACK)
    text_rect = text_surface.get_rect(center=(WINDOW_SIZE[0] // 2, WINDOW_SIZE[1] // 3))
    window.blit(text_surface, text_rect)
    draw_return_button()
    pygame.display.flip()
    game_over = True

def show_gameplay_screen():
    global player_hp
    global enemy_hp
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
    draw_ability_button_lock(20, list(battle_pokemon.ability.keys())[0])
    draw_ability_button_lock(110, list(battle_pokemon.ability.keys())[1])

    # Health Bars
    # Player's Health
    pygame.draw.line(window, BLACK, (100, (WINDOW_SIZE[1] - hud_height - 80)), ((WINDOW_SIZE[0] - 300), (WINDOW_SIZE[1] - hud_height - 80)), 6)
    text_surface = underline_font.render("Player 1", True, BLACK)
    window.blit(text_surface, (100, (WINDOW_SIZE[1] - hud_height - 140)))
    # p_health = 100
    text_surface = font.render("Health: " + str(player_hp), True, BLACK)
    window.blit(text_surface, (100, (WINDOW_SIZE[1] - hud_height - 110)))
    # Enemy's Health
    pygame.draw.line(window, BLACK, (300, 100), ((WINDOW_SIZE[0] - 100), 100), 6)
    text_surface = underline_font.render("Player 2", True, BLACK)
    text_rect = text_surface.get_rect()
    text_rect.top, text_rect.right = 40, (WINDOW_SIZE[0] - 100)
    window.blit(text_surface,text_rect)
    # p_health = 100
    text_surface = font.render("Health: " + str(enemy_hp), True, BLACK)
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

    # Energy Counter + Timer 
    global global_threads
    if len(global_threads) == 0:
        counter_thread = threading.Thread(target=energy_counter)
        global_threads.append(counter_thread)
        global_threads[0].start()


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

def draw_lobby_screen():
    window.fill(WHITE)
    draw_button()
    pygame.display.flip()

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
        ready_locked_in = False
        ability_locked_in = False

        draw_lobby_screen()

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    # For Ready Button
                    if not ready_locked_in:
                        button_rect = pygame.Rect(300, 270, 200, 60)

                        if button_rect.collidepoint(mouse_pos):
                            # lock the button and send ready message to server
                            ready_locked_in = True
                            draw_button_lock()
                            ready_message = "ready"
                            client_socket.send(ready_message.encode("utf-8"))

                    elif game_over:
                        button_rect = pygame.Rect(300, 270, 200, 60)

                        if button_rect.collidepoint(mouse_pos):
                            # lock the button and send ready message to server
                            return_message = "return"
                            client_socket.send(return_message.encode("utf-8"))
                            game_over = False
                            ready_locked_in = False
                            global_threads[0].join()
                            global_threads.clear()
                            current_energy = 0
                            player_hp = 100
                            enemy_hp = 100
                            draw_lobby_screen()
                    # For Clicking Abiltiies in Battle
                    else:
                        # Grab ability dmgs and names
                        ability1_dmg = battle_pokemon.ability[list(battle_pokemon.ability)[0]]
                        ability1_name = list(battle_pokemon.ability)[0]
                        ability2_dmg = battle_pokemon.ability[list(battle_pokemon.ability)[1]]
                        ability2_name = list(battle_pokemon.ability)[1]

                        # Locations of where the abilities are on the screen
                        ability1_rect = pygame.Rect(50, 520, 180, 60) 
                        ability2_rect = pygame.Rect(50, 430, 180, 60)

                        # Checks if ability is not greyed out, and if they clicked on the button
                        if (ability1_rect.collidepoint(mouse_pos)) and (ability_lock[list(battle_pokemon.ability)[0]] == False):
                            # Update Current Energy Value
                            current_energy -= ability1_dmg

                            # Send Attack message
                            dmg_message = f"attack:{ability1_name}:damage:{ability1_dmg}"
                            print(dmg_message)
                            client_socket.send(dmg_message.encode("utf-8"))
                        elif (ability2_rect.collidepoint(mouse_pos)) and (ability_lock[list(battle_pokemon.ability)[1]] == False):
                            # Update Current Energy Value
                            current_energy -= ability2_dmg

                            # Send Attack message
                            dmg_message = f"attack:{ability2_name}:damage:{ability2_dmg}"
                            print(dmg_message)
                            client_socket.send(dmg_message.encode("utf-8"))

                        # Greys out ability buttons if now the updated energy is less than cost
                        if current_energy < ability1_dmg:
                            draw_ability_button_lock(20, list(battle_pokemon.ability)[0])
                        if current_energy < ability2_dmg:
                            draw_ability_button_lock(110, list(battle_pokemon.ability)[1])

        # Close the client socket and quit Pygame when the loop ends
        client_socket.close()
        pygame.quit()