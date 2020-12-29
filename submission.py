# Imports helper functions
from kaggle_environments.envs.halite.helpers import *
from random import choice
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

def is_occupy_shipyard(ships,shipyard):
    for ship in ships:
        if ship.position == shipyard.position:
            return True
    return False


def is_occupy_cell(cell,ships):
    for ship in ships:
        if ship.position == cell:
            return True
    return False


def getDirTo(fromPos, toPos, size):
    fromX, fromY = divmod(fromPos[0],size), divmod(fromPos[1],size)
    toX, toY = divmod(toPos[0],size), divmod(toPos[1],size)
    if fromY < toY: return ShipAction.NORTH
    if fromY > toY: return ShipAction.SOUTH
    if fromX < toX: return ShipAction.EAST
    if fromX > toX: return ShipAction.WEST

def convert_to_point(Action):
    if Action == ShipAction.NORTH :return (0, 1)
    if Action == ShipAction.EAST :return (1, 0)
    if Action == ShipAction.SOUTH :return (0, -1)
    if Action == ShipAction.WEST: return (-1, 0)

def calculate_pos(position, offset):
    x = position[0]+offset[0]
    y = position[1]+offset[1]
    return (x,y)

def is_ship_full(ship,MAX_COLLECT):
    if ship.halite > MAX_COLLECT:
        return True
    return False

def is_ready_to_move(cell,MAX_halit_cell):
    if cell.halite < MAX_halit_cell : 
        return True
    return False

def Direction_invert(Action):
    if Action == ShipAction.NORTH :return ShipAction.EAST
    if Action == ShipAction.EAST :return ShipAction.SOUTH
    if Action == ShipAction.SOUTH :return ShipAction.WEST
    if Action == ShipAction.WEST: return ShipAction.NORTH

def destroyed_ship(ship_ids,ship_states):
    for ship_id in ship_states:
        if ship_id not in ship_ids:
            ship_states[ship_id] = "DESTROYED"
        
        
        if ship_states.get(ship_id) == "DESTROYED":
            del ship_states[ship_id]


def normalize(source,size):
    return (source[0] % size,source[1] % size)

def get_target_direction(source, target):
        """
        Returns where in the cardinality spectrum the target is from source. e.g.: North, East; South, West; etc.
        NOTE: Ignores toroid
        :param source: The source position
        :param target: The target position
        :return: A tuple containing the target Direction. A tuple item (or both) could be None if within same coords
        """
        return (ShipAction.NORTH if target[1] > source[1] else ShipAction.SOUTH if target[1] < source[1] else None,
                ShipAction.EAST if target[0] > source[0] else ShipAction.WEST if target[0] < source[0] else None)


def get_unsafe_moves(size, source, destination):
        """
        Return the Direction(s) to move closer to the target point, or empty if the points are the same.
        :param source: The starting position
        :param destination: The destination towards which you wish to move your object.
        :return: A list of valid (closest) Directions towards your target.
        """
        source = normalize(source,size)
        destination = normalize(destination,size)
        possible_moves = []
        distance = (abs(destination[0]-source[0]), abs(destination[1]-source[1]))
        y_cardinality, x_cardinality = get_target_direction(source, destination)

        if distance[0] != 0:
            possible_moves.append(x_cardinality if distance[0] < (size)
                                  else Direction_invert(x_cardinality))
        if distance[1] != 0:
            possible_moves.append(y_cardinality if distance[1] < (size)
                                  else Direction_invert(y_cardinality))
        return possible_moves
     
def eucl_dist(fromPos,ToPos):
    x_1 = pow((ToPos[0]-fromPos[0]),2)
    x_2 = pow((ToPos[1]-fromPos[1]),2)
    return sqrt(x_1+x_2)
        #print(" X1 =" + str(x_1) +" X_2 = "+ str(x_2) )



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
 
