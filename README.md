# 371-Python-Pokemon-Battler
## Run app
```
python server.py
python client.py
```
## Meeting Times
Thursdays and Sundays 1pm PST

## Language/Framework
- python + pygame

## Iteration 1 Notes
1. Implement Lobby and player connections - DONE
    - Player 1 starts the server and joins as client
    - Player 2 joins the server as a client
    - Ensure Server has connections to both clients

2. Implement Application-Layer messaging for server - ALMOST DONE
    - Simple client-side UI (ready button)
    - sends a 'ready' message to server
    - server receives 'ready' message notes that on the player object
    - when both players send ready messages, match begins

3. Combat Phase - TODO
    - Energy counter starts on the server
    - Each client has 2 abilities
    - When an ability is selected, sends an 'attack' message to server
    - Server receives 'attack' message
        - energy counter pauses
        - 'attacking' object locked
        - calculations are done
        - 'damage display' messages sent to both clients
        - 'attacking' object unlocked

## Saturday, July 22, 2023 Changelog
- Implemented basic lobby socket connection functionality in terminal mode
- Implemented basic ready check and simulated game start
- Created application-layer messaging scheme of splitting headers and payloads with ":"
### Things still to do:
- create pygame window in client.py to transfer from terminal to gui-style application
- add guards and safety checks for connection-related issues (disconnects, pre-emptive ready check, etc.)
- flesh out Player class and implement battle system