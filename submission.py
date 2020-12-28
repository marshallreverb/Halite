# Imports helper functions
from kaggle_environments.envs.halite.helpers import *
from random import choice
from utils import *
from math import *
# Returns best direction to move from one position (fromPos) to another (toPos)
# Example: If I'm at pos 0 and want to get to pos 55, which direction should I choose?
   
# Directions a ship can move[ North ,East , South ,WEST ]
directions_point = [(0, 1),(1, 0),(0,-1),(-1,0)]
directions = [ ShipAction.NORTH,ShipAction.EAST,ShipAction.SOUTH,ShipAction.WEST,]
MAX_RATIO = 13   #Max spawn ship ration
TOTALSTEPS = 400
MAX_SHIPYARD_DIST = 5
MAX_SHIPYARD = 5
MAX_COLLECT = 220
MAX_halit_cell = 35
# Will keep track of whether a ship is collecting halite or carrying cargo to a shipyard or 
ship_states = {}
pending_ship = {}

def req_dis(player,ship):
    counter = 0
    for shipyard in player.shipyards:
        dist = eucl_dist(ship.position,shipyard.position)
        if dist > MAX_SHIPYARD_DIST :
             counter = counter + 1
    if counter == len(player.shipyards):
        return True
    return False

def closest_dist(player,ship):
    mini = eucl_dist(ship.position,player.shipyards[0].position)
    i,index_ = 0,0
    for shipyard in player.shipyards:
        dist = eucl_dist(ship.position,shipyard.position)
        if mini > dist:
            mini = dist
            index_ = i
        i = i + 1
    return index_

def Collect(ship,target,player,shp_index):
     
                if is_ready_to_move(ship.cell,MAX_halit_cell):
                    surr_halite = [ship.cell.north.halite,ship.cell.east.halite,ship.cell.south.halite,ship.cell.west.halite]
                    maxi = max(range(len(surr_halite)), key=surr_halite.__getitem__)
                    mini = min(range(len(surr_halite)), key=surr_halite.__getitem__)
                    best = choice([maxi,mini])
                    #check si la prochaine direction n'est pas une direction cible
                    target_pos = calculate_pos(ship.position,directions_point[best])
                    if target_pos not in target.values() and not is_occupy_cell(target_pos,player.ships) and not target_pos == player.shipyards[shp_index].position :
                        target[ship.id] = target_pos
                        ship.next_action = directions[best]
                    else:
                        ship_states[ship.id] = "PENDING"
                        pending_ship[ship.id] = ship.position
                else:
                    ship_states[ship.id] = "COLLECT"    
                    pending_ship[ship.id] = ship.position

def Deposit(player,shipyd_idx,target,ship_states,ship,size):
     # randomly assign the shipyard
               # if len(player.shipyards) > 1:
                #    shipyard_indx = choice(range(0,(len(player.shipyards))))

               # else :
                #    shipyard_indx = shipyd_idx            
                #init
                # 
                shipyard_indx = closest_dist(player,ship)           
                #init
                #  
                target_pos = 0
                next_action = 0 

                moves   = get_unsafe_moves(size,ship.position,player.shipyards[shipyard_indx].position)
                for move in moves:
                    target_pos = calculate_pos(ship.position,convert_to_point(move))
                    if target_pos not in target.values() and not is_occupy_cell(target_pos,player.ships) and not is_occupy_shipyard(player.ships,player.shipyards[shipyard_indx]):
                        next_action = move
                        break
                if next_action != 0 :
                    target[ship.id] = target_pos 
                    ship.next_action = next_action
                else:
                    ship_states[ship.id] = "PENDING"
                    pending_ship[ship.id] = ship.position

def DepositE(player,shipyd_idx,target,ship_states,ship,size):
     # randomly assign the shipyard
               # if len(player.shipyards) > 1:
                #    shipyard_indx = choice(range(0,(len(player.shipyards))))

               # else :
                #    shipyard_indx = shipyd_idx            
                #init
                # 
                shipyard_indx = closest_dist(player,ship)           
                #init
                #  
                target_pos = 0
                next_action = 0 

                moves   = get_unsafe_moves(size,ship.position,player.shipyards[shipyard_indx].position)
                for move in moves:
                    target_pos = calculate_pos(ship.position,convert_to_point(move))
                    if target_pos not in target.values() and  is_occupy_cell(target_pos,player.ships) or target_pos == player.shipyards[shipyard_indx].position :
                        next_action = move
                        break
                if next_action != 0 :
                    target[ship.id] = target_pos 
                    ship.next_action = next_action
                else:
                    ship_states[ship.id] = "PENDING"
                    pending_ship[ship.id] = ship.position




# Returns the commands we send to our ships and shipyards
def agent(obs, config):
    size = config.size
    board = Board(obs, config)
    me = board.current_player
    end_sy = (len(me.shipyards)-1)
    #Beginning SHIPyard convert
    if len(me.shipyards) == 0 and len(me.ships) > 0 :
        me.ships[0].next_action = ShipAction.CONVERT
    
    #SPAWN
    
    if len(me.shipyards) != 0 :
        rd_sy = choice(range(0,end_sy+1))
        if  len(me.ships) < int(MAX_RATIO*(len(me.shipyards)) ) and not is_occupy_shipyard(me.ships,me.shipyards[rd_sy]) and board.step < 300:
            me.shipyards[rd_sy].next_action = ShipyardAction.SPAWN
     

    if board.step > int(TOTALSTEPS/7.5) and len(me.shipyards) != 0 and len(me.shipyards) < MAX_SHIPYARD:
        for ship in me.ships :
            if req_dis(me,ship):
                ship.next_action = ShipAction.CONVERT
                break 
            



    target = {}
    # Simple Ship state
    for ship in me.ships:
        if ship.next_action == None and len(me.shipyards) !=0:
            if board.step > 390:
                ship_states[ship.id] = "DEPOSITE"
            elif not is_ship_full(ship,MAX_COLLECT) : 
                ship_states[ship.id] = "COLLECT"
            else:
                ship_states[ship.id] = "DEPOSIT"

            #define Wait state 
           

            if ship_states.get(ship.id) == "COLLECT":
                Collect(ship,target,me,end_sy)

            if ship_states.get(ship.id) == "DEPOSIT": 
               Deposit(me,end_sy,target,ship_states,ship,size)
            
            if ship_states.get(ship.id) == "DEPOSITE": 
               DepositE(me,end_sy,target,ship_states,ship,size)
            

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
 
