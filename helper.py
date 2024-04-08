from pydantic import BaseModel
import random
import string
import hashlib as h
import json

class Mine(BaseModel):
    serial: str = None
    x: int = None
    y: int = None

class Rover(BaseModel):
    rover_id: str
    commands: str
    status: str

class RoverReq(BaseModel):
    commands:str

def getMap(filename):

    # Read in the array
    with open(filename, 'r') as f:
        # Skip the first line, we don't need it
        #next(f)
        map = [line.split() for line in f]

    return map

def updateFile(path_map: list[list[str]], file_name: str):
    with open(file_name, "w") as file:
        for row in path_map:
            file.write(' '.join(map(str, row)) + '\n')

def update_rovers_file(rovers: list[Rover], filename: str) -> None:
  # Convert the list of rovers to a JSON serializable list
    rover_data = [rover.model_dump() for rover in rovers]

    with open(filename, "w") as f:
        json.dump(rover_data, f, indent=4)  # Write with indentation for readability

def get_rovers_list(filename: str) -> list[Rover]:
    try:
        with open(filename, "r") as f:
            rover_data = json.load(f)
    except FileNotFoundError:
        print(f"File '{filename}' not found. Returning an empty list.")
        return []

    # Convert the list of dictionaries back to Rover objects
    rovers = [Rover(**data) for data in rover_data]  # Unpack data into Rover objects
    return rovers


def generate_serial_number():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))


def generate_pin():
    return ''.join(random.choices(string.digits + string.digits, k=10))


def hash_key(key: str):
    return h.sha256(key.encode('utf-8')).hexdigest()

def getMinesInfo(array):
    mines_info = []

    # Iterate over each cell in the array
    for i in range(len(array)):
        for j in range(len(array[i])):

            # If the cell contains code with length > 1, it's a mine serial num
            if isinstance(array[i][j], str) and len(array[i][j]) > 1:

                # Create a new Mine model with the code and coordinates
                mine = Mine(serial=array[i][j], x=i, y=j)

                # Add the new Mine model to the list
                mines_info.append(mine)

    return mines_info

def findMineInfoById(array,serial_id):
    for i in range(len(array)):
        for j in range(len(array[i])):
            if array[i][j]==serial_id:
                return Mine(serial=array[i][j], x=i, y=j)
    
    return Mine(serial="Not found", x = 0, y = 0)

                
def mine_delete(mine_file,serial_id):
    map = getMap("map.txt")
    for i in range(len(mine_file)):
        for j in range(len(mine_file[i])):
            if mine_file[i][j]==serial_id:
                mine_file[i][j]=0
                map[i][j]=0
                updateFile(mine_file,"mines.txt")
                updateFile(map, "map.txt")
                return "Mine deleted successfully!"
    return "Mine Not found"

def create_mine(serial,x,y):
    map = getMap("map.txt")
    
    map[x][y] = "1"
    updateFile(map,"map.txt")
    
    mine_map = getMap("mines.txt")
    mine_map[x][y] = serial

    updateFile(mine_map,"mines.txt")

    return serial

def updateMineInfo(serial:str,new_serial:str=None,x:int=None,y:int=None):
    mine_map = getMap("mines.txt")
    map = getMap("map.txt")
    new_mine= Mine() 
     
    for row_index, row in enumerate(mine_map): # Iterate through the mine map
        for col_index, map_serial in enumerate(row):
            if map_serial == serial: # ------------- Found a matching entry using serial num
                
                # Update with NEW serial number if given
                if new_serial is not None:
                    mine_map[row_index][col_index] = new_serial
                    new_mine.serial = new_serial

                # Update with NEW coordinates if given (X)
                if x is not None:
                    if 0 <= x < len(mine_map[0]): # Check new X-coordinate is valid  
                        mine_map[row_index][col_index] = (new_serial if new_serial else map_serial, x)  
                        map[row_index][col_index] = 1
                        new_mine.x = x
                    else:
                        print(f"Invalid X-coordinate: {x}. Mine coordinates: ({row_index}, {col_index})")

                # Update with NEW coordinates if given (Y)
                if y is not None:
                    if 0 <= y < len(mine_map): # Ensure new Y-coordinate is within valid bounds
                        mine_map[row_index][col_index] = (new_serial if new_serial else map_serial, y)  
                        map[row_index][col_index] = 1
                        new_mine.y = y
                    else:
                        print(f"Invalid Y-coordinate: {y}. Mine coordinates: ({row_index}, {col_index})")
                
                updateFile(mine_map,"mines.txt")
                updateFile(map,"map.txt")
                return new_mine # Update successful

    # Entry not found
    print(f"Could not find '{serial}' in  map.")
    return False
    
    
def find_rover_by_id(rover_id:str):
    rover_list = get_rovers_list("rovers.json")
    
    for rover in rover_list:
        if rover.rover_id == rover_id:
            return rover  # Return the rover object if ID matches

    return None  # Rover not found

def add_new_rover(commands:str):
    roversList = get_rovers_list("rovers.json")
    new_id = int(roversList[-1].rover_id)+1
    new_rover = Rover(rover_id=str(new_id),commands=commands,status="Not started")
    roversList.append(new_rover)
    update_rovers_file(rovers=roversList,filename="rovers.json")
    return int(new_rover.rover_id)

def delete_rover(rover_id:str):
    roversList = get_rovers_list("rovers.json")
    for rover in roversList:
        if rover.rover_id == rover_id:
            roversList.remove(rover)
            update_rovers_file(rovers=roversList,filename="rovers.json")
            return "Deleted Rover"
    return "Rover not found"

def send_commands(rover_id: str, commands: str):
    roversList = get_rovers_list("rovers.json")
    for rover in roversList:
        if rover.rover_id == rover_id:
            if rover.status == "Not started" or rover.status == "Finished":
                rover.commands = commands
                update_rovers_file(roversList,"rovers.json")
                return "New Commands sent"
    return "Failure to send new commands"


# Rover helper methods ---------------------------------------------------------------------------------------------------
def check_boundary(current_dir, x, y, x_border, y_border):
    # Hash map with direction and their boundary condition
    boundaries = {'S': (y + 1 < y_border), 'N': (y - 1 >= 0), 'E': (x + 1 < x_border), 'W': (x - 1 >= 0)}
    # Using the current_dir as a key I return whether the boundary passes or fails (T or F)
    return boundaries.get(current_dir, False)


def disarm_mine(mine_map: list[list[str]], y: int, x: int):
    # make the key
    key = generate_pin() + mine_map[y][x]
    # Hash the key
    hk = hash_key(key)
    while hk[:2] != '00':
        hk = hash_key(key)
        print(f"Attempting with {hk}")
        key = generate_pin() + mine_map[y][x]


def change_direction(dir_facing: str, turn: str):
    directions = ['N', 'E', 'S', 'W']
    index = directions.index(dir_facing)
    # make use of pythons negative indexing :)
    new_idx = (index + 1) % 4 if turn == 'R' else (index - 1) % 4

    return directions[new_idx]

def update_rover_list(rover:Rover):
    rover_list = get_rovers_list("rovers.json")
    
    for r in rover_list:
        if r.rover_id == rover.rover_id:
            r.status = rover.status
            update_rovers_file(rovers=rover_list,filename="rovers.json")
            return 
    
    

                
def start_traverse(rover_id:str):
    
    map = getMap("map.txt")
    mine_map = getMap("mines.txt")
    # print(f"Rover ID: {rover_id}")
    rover = find_rover_by_id(rover_id)
    
    if rover == None:
        return "Failure to find the Rover"
    
    rover.status = "Roaming Maze"
    update_rover_list(rover=rover)

    y, x = 0, 0
    current_dir = 'S'

    # print(f"Rover: {rover.rover_id}")
    
    for m in rover.commands:
        # disarming the mine
        if map[y][x] == '1' and m == 'D':
            disarm_mine(mine_map, y, x)
            map[y][x] = "#"

        elif m == 'M' and check_boundary(current_dir, x, y, len(map[y]), len(map)):
            # check if I can actually move off the mine
            if map[y][x] == '1':
                map[y][x] = "x"
                print("You died!!")
                rover.status = "Finished"
                update_rover_list(rover=rover)
                break
            else:
                # update position
                if map[y][x] != '#':
                    map[y][x] = "*"
    
                # Hash map has a tuple containing the directional move in terms of a 2D array
                directions = {'S': (0, 1), 'N': (0, -1), 'E': (1, 0), 'W': (-1, 0)}

                dx, dy = directions[current_dir]

                x = min(max(x + dx, 0), len(map[0]) - 1)
                y = min(max(y + dy, 0), len(map) - 1)

        # change direction
        elif m == 'R' or m == 'L':
            current_dir = change_direction(current_dir, m)
    
    rover.status = "Finished"
    update_rover_list(rover=rover)
    
    for row in map:
        print(f"Row: {row}")

    return map