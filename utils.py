# Imports helper functions
from kaggle_environments.envs.halite.helpers import *
from math import *

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

