from fastapi import FastAPI,Body
from fastapi.middleware.cors import CORSMiddleware
from helper import findMineInfoById, getMap,getMinesInfo,Mine
from helper import mine_delete,create_mine,updateMineInfo
from helper import get_rovers_list,find_rover_by_id,add_new_rover,delete_rover,send_commands,start_traverse,RoverReq

app = FastAPI()

origins = [
    "http://localhost:8000",
    "http://localhost:3000",
    "http://127.0.0.1:8000",
    "http://127.0.0.1:3000",
    "http://localhost:80",
    "http://127.0.0.1:80",
    "http://localhost",
    "null",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------------------------------------------------------------------- Map Requests 
# --------------------------------------------------------------- GET Map 
@app.get("/map")
async def get_map():
    map = getMap("map.txt")
    print(map)
    return map

# --------------------------------------------------------------- UPDATE Map 
@app.put("/map")
async def put_map(height:int,width:int):
    # To update the height and width of the field
    array = getMap("map.txt")
    old_height = len(array)
    old_width = len(array[0]) if old_height > 0 else 0

    # Initialize new array with None
    new_array = [["0" for _ in range(width)] for _ in range(height)]

    # Copy old data into new array
    for i in range(min(old_height, height)):
        for j in range(min(old_width, width)):
            new_array[i][j] = array[i][j]
    
    # Write new_array to a new file
    with open("new_map_with_updated_values.txt", "w") as f:
        for row in new_array:
            f.write(" ".join(row) + "\n")
    
    return new_array


# ------------------------------------------------------------------------------------------------ Mines Requests 
# ---------------------------------------------------- GET ALL mines - Serial number & Coordinates 
@app.get("/mines")
def getAllMineInfo():
    serial_map = getMap("mines.txt")    
    print("Printing the serial and coordinates")
    mineAndCoordinateModel = getMinesInfo(serial_map)
    print(mineAndCoordinateModel)
    return mineAndCoordinateModel

# ---------------------------------------------------- GET a mine - Serial number & Coordinates by ID
@app.get("/mines/{id}")
def getMineInfoById(id:str):
    return findMineInfoById(getMap("mines.txt"),id)

# ---------------------------------------------------- DELETE a mine using ID
@app.delete("/mines/{id}")
def deleteMineById(id:str):
    return mine_delete(getMap("mines.txt"),id)

# ---------------------------------------------------- CREATE a mine using ID & coordinates
@app.post("/mines")
def createMine(mine:Mine= Body(...)):
    print(mine)
    new_mine = create_mine(mine.serial,mine.x,mine.y)
    return new_mine

# ---------------------------------------------------- UPDATE a mine using ID & coordinates
@app.put("/mines/{id}")
def updateMine(id:str,serial:str=None,x:int=None,y:int=None):
    return updateMineInfo(id,serial,x,y)


# ------------------------------------------------------------------------------------------------ Rover Requests 
# ---------------------------------------------------- GET Rovers list
@app.get("/rovers")
def getAllRovers():
    return get_rovers_list("rovers.json")

# ---------------------------------------------------- GET rover Info by Id
@app.get("/rovers/{rover_id}")
def getRoverInfoById(rover_id: str):
    return find_rover_by_id(rover_id)

# ---------------------------------------------------- CREATE new rover
@app.post("/rovers")
def createRover(rover:RoverReq= Body(...)):
    return add_new_rover(rover.commands)

# ---------------------------------------------------- DELETE a rover by Id
@app.delete("/rovers/{rover_id}")
def deleteRover(rover_id: str):
    return delete_rover(rover_id)

# ---------------------------------------------------- SEND string commands to rover by Id
@app.put("/rovers/{rover_id}")
def sendCommands(rover_id: str, commands: str):
    return send_commands(rover_id,commands)

# ---------------------------------------------------- START rover 
@app.post("/rovers/{rover_id}/dispatch")
def dispatchRover(rover_id: str):
    return start_traverse(rover_id=rover_id)