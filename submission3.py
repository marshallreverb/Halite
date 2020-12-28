# Imports helper functions
from kaggle_environments.envs.halite.helpers import *
from random import choice
# Returns best direction to move from one position (fromPos) to another (toPos)
# Example: If I'm at pos 0 and want to get to pos 55, which direction should I choose?
from utils import *

# Directions a ship can move[ North ,East , South ,WEST ]
directions_point = [(0, 1),(1, 0),(0,-1),(-1,0)]
directions = [ ShipAction.NORTH,ShipAction.EAST,ShipAction.SOUTH,ShipAction.WEST,]
MAX_RATIO = 5
MAX_COLLECT = 250
MAX_halit_cell = 20
# Will keep track of whether a ship is collecting halite or carrying cargo to a shipyard or 
ship_states = {}
pending_ship = {}

# Returns the commands we send to our ships and shipyards
def agent(obs, config):
    size = config.size
    board = Board(obs, config)
    me = board.current_player
    

    #refresh state 
    #destroyed_ship(me.ship_ids,ship_states)
       #Shipyard
    if len(me.shipyards) == 0 and len(me.ships) > 0 :
        me.ships[0].next_action = ShipAction.CONVERT
    #SPAWN
    if len(me.shipyards) != 0 and len(me.ships) < int(MAX_RATIO/(len(me.shipyards)+1)) and not is_occupy_shipyard(me.ships,me.shipyards[0]):
        me.shipyards[0].next_action = ShipyardAction.SPAWN
     
    target = {}
    # Simple Ship state
    for ship in me.ships:
        if ship.next_action == None and len(me.shipyards) !=0:

            if not is_ship_full(ship,MAX_COLLECT) : 
                ship_states[ship.id] = "COLLECT"
            else:
                ship_states[ship.id] = "DEPOSIT"

            #define Wait state 
            if ship_states.get(ship.id) == "COLLECT":
                if is_ready_to_move(ship.cell,MAX_halit_cell):
                    surr_halite = [ship.cell.north.halite,ship.cell.east.halite,ship.cell.south.halite,ship.cell.west.halite]
                    maxi = max(range(len(surr_halite)), key=surr_halite.__getitem__)
                    mini = min(range(len(surr_halite)), key=surr_halite.__getitem__)
                    best = choice([maxi,mini])
                    #check si la prochaine direction n'est pas une direction cible
                    target_pos = calculate_pos(ship.position,directions_point[best])
                    if target_pos not in target.values() and not is_occupy_cell(target_pos,me.ships) and not target_pos == me.shipyards[0].position :
                        target[ship.id] = target_pos
                        ship.next_action = directions[best]
                    else:
                        ship_states[ship.id] = "PENDING"
                        pending_ship[ship.id] = ship.position
                else:
                    ship_states[ship.id] = "COLLECT"    
                    pending_ship[ship.id] = ship.position



            if ship_states.get(ship.id) == "DEPOSIT": 
                target_pos = 0
                next_action = 0 
                moves = get_unsafe_moves(size,ship.position,me.shipyards[0].position)
                for move in moves:
                    target_pos = calculate_pos(ship.position,convert_to_point(move))
                    if target_pos not in target.values() and not is_occupy_cell(target_pos,me.ships):
                        next_action = move
                        break
                if next_action != 0 :
                    target[ship.id] = target_pos 
                    ship.next_action = next_action
                else:
                    ship_states[ship.id] = "PENDING"
                    pending_ship[ship.id] = ship.position
                
            

            if ship_states.get(ship.id) == "PENDING":
                for ship_id in pending_ship:
                    if ship.id == ship_id : 
                        next_offset = getDirTo(ship.position,pending_ship.get(ship_id),size)
                        ship.next_action = next_offset
                        ship_states[ship.id] = "COLLECT"
                    

    #print("Step : "+ str(board.step))
    #for id in me.ship_ids:
    #    print("Ship Id "+ str(id) + "state :" + str(ship_states.get(id)))

    return me.next_actions
 
