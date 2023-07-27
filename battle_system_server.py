#psudocode

#action dictionary is stored server side and has a message for each action

#each player has a health value
#p1 = player1
#p2 = player2 

#when action is recieved from client (action, damage){
# sets a lock so no more actions can be recieved
#target.health -= damage
#send action result to client (action, action:message, target, updated_health)
#if target.health <= 0:
# send game over message to each client (win/loss)
# unlock action recieving
