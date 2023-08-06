import socket
import threading
import requests
import pygame
import random
import pickle
from collections import deque
from models.pokemon import Pokemon
from io import BytesIO

# Global Varaibles
battle_pokemon = Pokemon("", {}, 0, 0)
enemy_pokemon = Pokemon("", {}, 0, 0)
ability_lock = {}
current_energy = 0
my_pokemon_image = None
enemy_pokemon_image = None
boosted_pokemon_image = None
enemy_boosted_pokemon_image = None
attack_lock = False #if there is an attack in progress
boost_lock = False
game_over = False
player_hp = 100
enemy_hp = 100
global_threads = []
ball_state = random_numbers = random.sample(range(10), 3)
selected_ball = 0
boosted = False
enemy_boosted = False
attack_log_history = deque()
attack_render_queue = 0

# incoming messages
def receive_message(sock):
    message_lock = threading.Lock()
    while True:
        try:
        # with message_lock:
            global attack_lock
            global player_hp
            global enemy_hp
            global boosted
            global my_pokemon_image
            global enemy_boosted
            global enemy_pokemon_image
            global boost_lock
            global attack_render_queue

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
                log_message = next(msg_iterator)
                attack_log_history.append(log_message)
                if len(attack_log_history) > 5:
                    attack_log_history.popleft()
                print(f"Log: {log_message}") #REMOVE
            # game_start header for starting the game
            elif header == "pokemon":
                global battle_pokemon 
                global enemy_pokemon
                battle_pokemon = pickle.loads(eval(next(msg_iterator)))
                enemy_pokemon = pickle.loads(eval(next(msg_iterator)))
            elif header == "game_start":
                print("loading game")
                show_gameplay_screen()
            # energy locking while attack occurring
            # TODO: disable inputs while energy_locked OR implement energy refund message from server
            elif header == "pause_counter":
                energy_locked = True
            elif header == "resume_counter":
                energy_locked = False
            elif header == "boost":
                boosted = True
                show_gameplay_screen()
            elif header == "enemy_boost":
                enemy_boosted = True
                boost_lock = True
                show_gameplay_screen()
            elif header == "boost_end":
                boosted = False
                show_gameplay_screen()
            elif header == "enemy_boost_end":
                enemy_boosted = False
                boost_lock = False
                show_gameplay_screen()
            elif header == "lock":
                attack_lock = True
                attack_render_queue += 1
                draw_ability_button_lock(20, list(battle_pokemon.ability.keys())[0], False) #false means don't set the action_lock
                draw_ability_button_lock(110, list(battle_pokemon.ability.keys())[1], False)
            elif header == "unlock":
                attack_lock = False
            elif header == "hp_update":
                player_hp = int(next(msg_iterator))
                enemy_hp = int(next(msg_iterator))
                show_gameplay_screen()
            elif header == "game_over":
                print("game_over received")
                win_state = next(msg_iterator)
                render_game_over_screen(win_state) 
            # the client id and even/odd check are used to display two different ready status line
            elif header == "ready_display":
                player_id = next(msg_iterator)
                ready_status = next(msg_iterator)
                print(ready_status)
                if int(player_id) % 2 == 0:
                    display_ready_status_top(ready_status)
                else:
                    display_ready_status_bottom(ready_status)
            # for displaying countdown timer until game start
            elif header == "count_down":
                countdown = next(msg_iterator)
                print(countdown)
                count_down(countdown)



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
RED = (255, 0, 0)
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


def count_down(countdown):
    # Clear the previous text by filling with the background color
    clear = pygame.Rect((0, WINDOW_SIZE[1] - 600), (WINDOW_SIZE[0], 100))
    window.fill(WHITE, clear)

    # Render and display the new countdown value
    font = pygame.font.Font(None, 70)
    text_surface = font.render(countdown, True, BLACK)
    text_rect = text_surface.get_rect(center=(WINDOW_SIZE[0] // 2, WINDOW_SIZE[1] // 2))
    text_rect.bottom = WINDOW_SIZE[1] - 500
    window.blit(text_surface, text_rect)
    pygame.display.flip()

# display the first player's ready status
def display_ready_status_top(ready_status):
    font = pygame.font.Font(None, 36)
    text_surface = font.render(ready_status, True, BLACK)
    text_rect = text_surface.get_rect(center=(WINDOW_SIZE[0] // 2, WINDOW_SIZE[1] // 2))
    text_rect.bottom = WINDOW_SIZE[1] - 25
    window.blit(text_surface, text_rect)
    pygame.display.flip()

# display the second player's ready status
def display_ready_status_bottom(ready_status):
    font = pygame.font.Font(None, 36)
    text_surface = font.render(ready_status, True, BLACK)
    text_rect = text_surface.get_rect(center=(WINDOW_SIZE[0] // 2, WINDOW_SIZE[1] // 2))
    text_rect.bottom = WINDOW_SIZE[1] - 75
    window.blit(text_surface, text_rect)
    pygame.display.flip()

def draw_button():
    button_rect = pygame.Rect(300, 270, 200, 60)
    pygame.draw.rect(window, GREEN, button_rect)
    text_surface = font.render("Ready", True, WHITE)
    text_rect = text_surface.get_rect(center=button_rect.center)
    window.blit(text_surface, text_rect)

def draw_balls():
    scale_factor = 0.1
    img = pygame.image.load("./img/ball.png")
    img_width = int(img.get_width() * scale_factor)
    img_height = int(img.get_height() * scale_factor)
    img = pygame.transform.scale(img, (img_width, img_height))
    ball_button1 = pygame.Rect(250, 400, 60, 60)
    ball_button2 = pygame.Rect(365, 400, 60, 60)
    ball_button3 = pygame.Rect(480, 400, 60, 60)
    pygame.draw.circle(window, GREEN if selected_ball == 0 else WHITE, ball_button1.center, 30)
    pygame.draw.circle(window, GREEN if selected_ball == 1 else WHITE, ball_button2.center, 30)
    pygame.draw.circle(window, GREEN if selected_ball == 2 else WHITE, ball_button3.center, 30)
    ball_rect1 = img.get_rect(center=ball_button1.center)
    ball_rect2 = img.get_rect(center=ball_button2.center)
    ball_rect3 = img.get_rect(center=ball_button3.center)
    window.blit(img, ball_rect1)
    window.blit(img, ball_rect2)
    window.blit(img, ball_rect3)

    return selected_ball


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
def draw_ability_button_lock(padding, name, lock):
    # Update Ability lock to be True, so its  greyed out and unclickable
    if lock:
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
    global enemy_boosted
    global boosted
    global my_pokemon_image
    global boosted_pokemon_image
    global enemy_pokemon_image
    global enemy_boosted_pokemon_image
    global boost_lock
    global attack_lock
    global attack_render_queue
    global attack_log_history

    # Energy Counter box location
    box_size = 150
    energy_box = pygame.Rect(270, (WINDOW_SIZE[1] - box_size - 20), box_size, box_size)

    # Incrementing Energy Counter
    while True:
        if game_over:
            energy_locked = False
            my_pokemon_image = None
            boosted_pokemon_image = None
            enemy_pokemon_image = None
            enemy_boosted_pokemon_image = None
            boosted = False
            boost_lock = False
            enemy_boosted = False
            attack_lock = False
            attack_log_history.clear()
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
        if not attack_lock and current_energy  < 200:
            current_energy +=1
        clock.tick(10 if boosted else 5)

        # Change Ability Button Colours from Greyed if energy is available and not locked
        if current_energy >= ability_dmg[0] and not attack_lock:
            draw_ability_button(20, list(battle_pokemon.ability.keys())[0], MAGENTA)
        if current_energy >= ability_dmg[1] and not attack_lock:
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

def render_log(log_history):
    #Clear the logs, there is probably a better way to do this
    white_rect = pygame.Rect((WINDOW_SIZE[0] - 340), (WINDOW_SIZE[1] - 170), 300, 150)
    energy_box = pygame.Rect((WINDOW_SIZE[0] - 340), (WINDOW_SIZE[1] - 170), (WINDOW_SIZE[0] - (WINDOW_SIZE[0] - 270) + 20), 150)
    pygame.draw.rect(window, WHITE, white_rect, 0 , 3)
    pygame.draw.rect(window, BLACK, energy_box, 3 , 3)
    text_surface = attack_log_font.render("Attack Log", True, BLACK)
    window.blit(text_surface, ((WINDOW_SIZE[0] - 340 + 5), (WINDOW_SIZE[1] - 170 + 5)))

    #Render the updated logs
    font = pygame.font.Font(None, 18)
    for index, msg in enumerate(log_history):
        text_surface = font.render(msg, True, BLACK)
        text_x = WINDOW_SIZE[0] - 340 + 5  # X-coordinate inside the rect
        text_y = WINDOW_SIZE[1] - 170 + 30 + index * 25  # Y-coordinate inside the rect, 25 pixels down per line
        window.blit(text_surface, (text_x, text_y))

# Function to flash the attack message. 
def render_attack():
    global game_over
    global attack_render_queue
    while True:
        if game_over:
            break
        if attack_render_queue > 0:
            message = "Attack!"
            font = pygame.font.Font(None, 100)
            flashing = True
            flash_count = 0
            text_surface = font.render(message, True, RED)
            text_rect = text_surface.get_rect(center=(WINDOW_SIZE[0] // 2, WINDOW_SIZE[1] // 3))
            while flash_count < 6: # Flashes on 3 times, Flashes off 3 times
                if flashing:
                    window.blit(text_surface, text_rect)
                    pygame.display.update(text_rect)
                    pygame.time.wait(333)
                    flashing = False
                else:
                    window.fill(TAN, text_rect) # Fills the text rect with the background colour
                    pygame.display.update(text_rect)
                    pygame.time.wait(333)
                    flashing = True
                flash_count += 1
            attack_render_queue -= 1

def show_gameplay_screen():
    global enemy_hp
    global my_pokemon_image
    global boosted_pokemon_image
    global enemy_pokemon_image
    global enemy_boosted_pokemon_image
    global enemy_boosted
    global boosted
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
    draw_ability_button_lock(20, list(battle_pokemon.ability.keys())[0], True)
    draw_ability_button_lock(110, list(battle_pokemon.ability.keys())[1], True)
    # fetch pokemon img
    if my_pokemon_image == None:
        url = "https://pokeapi.co/api/v2/pokemon/" + str(battle_pokemon.number); 
        response = requests.get(url)
        img_data = response.json()["sprites"]["back_default"]
        my_pokemon_image = requests.get(img_data)
    if boosted and (boosted_pokemon_image  == None):
        url = "https://pokeapi.co/api/v2/pokemon/" + str(battle_pokemon.boosted_number); 
        response = requests.get(url)
        img_data = response.json()["sprites"]["back_default"]
        boosted_pokemon_image = requests.get(img_data)

    img = pygame.image.load(BytesIO(boosted_pokemon_image.content if boosted else my_pokemon_image.content))
    scale_factor = 2.7
    img_width = int(img.get_width() * scale_factor)
    img_height = int(img.get_height() * scale_factor)
    img = pygame.transform.scale(img, (img_width, img_height))
    my_pokemon_image_rect = pygame.Rect(-20, 170, 60, 60)
    window.blit(img, my_pokemon_image_rect)
    pygame.display.flip()

    if enemy_pokemon_image == None:
        url = "https://pokeapi.co/api/v2/pokemon/" + str(enemy_pokemon.number); 
        response = requests.get(url)
        img_data = response.json()["sprites"]["front_default"]
        enemy_pokemon_image= requests.get(img_data)

    if enemy_boosted and (enemy_boosted_pokemon_image == None):
        url = "https://pokeapi.co/api/v2/pokemon/" + str(enemy_pokemon.boosted_number); 
        response = requests.get(url)
        img_data = response.json()["sprites"]["front_default"]
        enemy_boosted_pokemon_image = requests.get(img_data)

    img = pygame.image.load(BytesIO(enemy_boosted_pokemon_image.content if enemy_boosted else enemy_pokemon_image.content))
    scale_factor = 2.7
    img_width = int(img.get_width() * scale_factor)
    img_height = int(img.get_height() * scale_factor)
    img = pygame.transform.scale(img, (img_width, img_height))
    enemy_pokemon_image_rect = pygame.Rect(550, -50, 60, 60)
    window.blit(img, enemy_pokemon_image_rect)
    pygame.display.flip()



    #boosted button
    if not boost_lock:
        scale_factor = 0.1
        img = pygame.image.load("./img/fire.png" if boosted else "./img/fire2.png")
        img_width = int(img.get_width() * scale_factor)
        img_height = int(img.get_height() * scale_factor)
        img = pygame.transform.scale(img, (img_width, img_height))
        boosted_button = pygame.Rect(720, 310, 60, 60)
        window.blit(img, boosted_button)

    render_log(attack_log_history)
    
    # Health Bars
    # Player's Health
    pygame.draw.line(window, BLACK, (230, (WINDOW_SIZE[1] - hud_height - 80)), ((WINDOW_SIZE[0] - 300), (WINDOW_SIZE[1] - hud_height - 80)), 6)
    text_surface = underline_font.render("Player 1", True, BLACK)
    window.blit(text_surface, (230, (WINDOW_SIZE[1] - hud_height - 140)))
    # p_health = 100
    text_surface = font.render("Health: " + str(player_hp), True, BLACK)
    window.blit(text_surface, (230, (WINDOW_SIZE[1] - hud_height - 110)))
    # Enemy's Health
    pygame.draw.line(window, BLACK, (300, 100), ((WINDOW_SIZE[0] - 200), 100), 6)
    text_surface = underline_font.render("Player 2", True, BLACK)
    text_rect = text_surface.get_rect()
    text_rect.top, text_rect.right = 40, (WINDOW_SIZE[0] - 200)
    window.blit(text_surface,text_rect)
    # p_health = 100
    text_surface = font.render("Health: " + str(enemy_hp), True, BLACK)
    text_rect = text_surface.get_rect()
    text_rect.top, text_rect.right = 70, (WINDOW_SIZE[0] - 200)
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
    if len(global_threads) == 0:
        counter_thread = threading.Thread(target=energy_counter)
        attack_render_thread = threading.Thread(target=render_attack)
        global_threads.append(counter_thread)
        global_threads.append(attack_render_thread)
        global_threads[0].start()
        global_threads[1].start()
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

def draw_lobby_screen():
    window.fill(WHITE)
    draw_button()
    draw_balls()
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
                        ball_button1 = pygame.Rect(250, 400, 60, 60)
                        ball_button2 = pygame.Rect(365, 400, 60, 60)
                        ball_button3 = pygame.Rect(480, 400, 60, 60)

                        # select pokemon for battle
                        if ball_button1.collidepoint(mouse_pos):
                            selected_ball = 0
                            window.fill(WHITE)
                            draw_button()
                            draw_balls()
                            pygame.display.flip()
                       
                        if ball_button2.collidepoint(mouse_pos):
                            selected_ball = 1
                            window.fill(WHITE)
                            draw_button()
                            draw_balls()
                            pygame.display.flip()
                        if ball_button3.collidepoint(mouse_pos):
                            selected_ball = 2
                            window.fill(WHITE)
                            draw_button()
                            draw_balls()
                            pygame.display.flip()
                        if button_rect.collidepoint(mouse_pos):
                            # lock the button and send ready message to server
                            ready_locked_in = True
                            draw_button_lock()
                            ready_message = f"ready:{ball_state[selected_ball]}"
                            client_socket.send(ready_message.encode("utf-8"))
                        

                    elif game_over:
                        button_rect = pygame.Rect(300, 270, 200, 60)

                        if button_rect.collidepoint(mouse_pos):
                            # lock the button and send ready message to server
                            return_message = "return"
                            client_socket.send(return_message.encode("utf-8"))
                            game_over = False
                            ready_locked_in = False
                            while len(global_threads) > 0:
                                global_threads[-1].join()
                                global_threads.pop()
                            current_energy = 0
                            player_hp = 100
                            enemy_hp = 100
                            draw_lobby_screen()
                    # For Clicking Abiltiies in Battle
                    else:
                        # Boost Pokemon
                        boosted_button = pygame.Rect(720, 310, 60, 60)

                        # Grab ability dmgs and names
                        while battle_pokemon.ability == {}:
                            continue
                        ability1_dmg = battle_pokemon.ability[list(battle_pokemon.ability)[0]]
                        ability1_name = list(battle_pokemon.ability)[0]
                        ability2_dmg = battle_pokemon.ability[list(battle_pokemon.ability)[1]]
                        ability2_name = list(battle_pokemon.ability)[1]

                        # Locations of where the abilities are on the screen
                        ability1_rect = pygame.Rect(50, 520, 180, 60) 
                        ability2_rect = pygame.Rect(50, 430, 180, 60)

                        # boost pokemon
                        if boosted_button.collidepoint(mouse_pos):
                            if current_energy > 15 and not boost_lock and not boosted:
                                boost_message ="boost"
                                print("try to boost !!!")
                                client_socket.send(boost_message.encode("utf-8"))
                            elif boosted:
                                boost_message ="stop_boost"
                                print("stop boosting !!!")
                                client_socket.send(boost_message.encode("utf-8"))
                            
                        # Checks if ability is not greyed out, and if they clicked on the button
                        if (ability1_rect.collidepoint(mouse_pos)) and (ability_lock[list(battle_pokemon.ability)[0]] == False) and (not attack_lock):
                            # Update Current Energy Value
                            current_energy -= ability1_dmg

                            # Send Attack message
                            dmg_message = f"attack:{ability1_name}:damage:{ability1_dmg}"
                            print(dmg_message)
                            client_socket.send(dmg_message.encode("utf-8"))
                        elif (ability2_rect.collidepoint(mouse_pos)) and (ability_lock[list(battle_pokemon.ability)[1]] == False) and (not attack_lock):
                            # Update Current Energy Value
                            current_energy -= ability2_dmg

                            # Send Attack message
                            dmg_message = f"attack:{ability2_name}:damage:{ability2_dmg}"
                            print(dmg_message)
                            client_socket.send(dmg_message.encode("utf-8"))

                        # Greys out ability buttons if now the updated energy is less than cost or if there is an attack going on
                        if current_energy < ability1_dmg or attack_lock:
                            draw_ability_button_lock(20, list(battle_pokemon.ability)[0], True)
                        if current_energy < ability1_dmg or attack_lock:
                            draw_ability_button_lock(110, list(battle_pokemon.ability)[1], True)


        # Close the client socket and quit Pygame when the loop ends
        client_socket.close()
        pygame.quit()