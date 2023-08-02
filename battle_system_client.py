#psudocode

#client side
#int energy
#energy = 0

#every 0.1 seconds {
# if energy < 1000{
# energy += 1
# update ui energy bar
#}

#when action is selected{
# if energy >= action_cost{
# send action (action, damage) to server
# energy -= action_cost
# }

#when action result is recieved from server (action, message, target, updated_health){
# {
# display action
# display message
# target.health = updated_health
# update ui health bar
# }

#when player recives game over message from server (win/loss{
# display win/loss message
# stop energy counter
#}
