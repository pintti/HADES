from flask import Flask, jsonify, request
from typing import List
import requests as req
import numpy as np
import heapq
import sys
import time
import pickle
import psycopg2


app = Flask(__name__)

processor_dict = {}

conn = None


@app.route("/connect", methods=["GET"])
def connect_processor():
    """Connects a new processor to the server and creates all necessary information to be processed"""
    if request.method == "GET":
        new_processor_id = len(processor_dict)
        area = create_area()
        processor_dict[new_processor_id] = {
            "area": area,
            "spawn": get_rand_point(area),
            "drones": {}
        }
        print("New processor added", file=sys.stderr, flush=True)
        add_new_processor(new_processor_id, area, processor_dict[new_processor_id]["spawn"])
        return str(new_processor_id), 200
    


@app.route("/add_drone", methods=["POST"])
def add_new_drone():
    """Adds a new drone to the network
    Requires the post JSON to have an id and a drone information"""
    if request.method == "POST":
        try:
            processor_id = request.json["id"]
            drone_json = request.json["drone"]
            processor_area = processor_dict[processor_id]["area"]
            steps = add_drone_to_processor(processor_id, drone_json, processor_area)
            return steps, 200
        except KeyError:
            return "No ID or Drone information", 400
        

@app.route("/drone", methods=["POST"])
def get_drone_step():
    """Get the drone step from processor and handle it correctly.
    Requires the JSON format to be in the next format:
    {"id": processor ID, "drone_id": drone ID, "drone_loc": location of the drone}"""
    if request.method == "POST":
        try:
            processor_id = request.json["id"]
            drone_id = request.json["drone_id"]
            drone_location = request.json["drone_loc"]
            success, msg = handle_drone_step(processor_id, drone_id, drone_location)
            if success:
                return msg, 200
            else:
                return msg, 400
        except KeyError:
            return "No ID or Drone information", 400


@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"


def handle_drone_step(processor_id, drone_id, drone_location):
    """Function for handling the new drone information. Updates new location and removes the required steps
    from drone dict."""
    try:
        drone_dict = processor_dict[processor_id]["drones"][drone_id]
        update_drone_loc_visual(drone_location, processor_id, drone_id)
        drone_dict["location"] = drone_location
        if drone_dict["steps"]:
            if drone_location in drone_dict["steps"]:
                drone_loc_index = drone_dict["steps"].index(drone_location)
                drone_dict["steps"] = drone_dict["steps"][drone_loc_index:]
        print_matrix_area(drone_location, processor_dict[processor_id]["area"])
        return True, "Drone step complete"
    except KeyError:
        return False, "ID not found!"


def update_drone_loc_visual(drone_location, processor_id, drone_id):
    old_loc = processor_dict[processor_id]["drones"][drone_id]["location"]
    processor_dict[processor_id]["area"][old_loc[0]][old_loc[1]][old_loc[2]] = 0
    processor_dict[processor_id]["area"][drone_location[0]][drone_location[1]][drone_location[2]] = drone_id
    print(old_loc, file=sys.stderr, flush=True)
    print(drone_location, file=sys.stderr, flush=True)


def add_drone_to_processor(processor_id, drone_info, processor_area):
    """Adds drone information to the dict
    Args:
        processor_id: int belonging to that processor
        drone_info: a json object containing information regarding the drone"""
    drone_id = drone_info["id"]
    drone_location = drone_info["location"]
    goal = get_rand_point(processor_area)
    processor_area[drone_location[0]][drone_location[1]][drone_location[2]] = drone_id
    processor_dict[processor_id]["drones"][drone_id] = {
        "location": drone_location,
        "goal": goal,
        "steps": get_drone_steps(drone_location, goal, processor_area),
        "moving": False
    }
    print_matrix_area(drone_location, processor_area)
    add_new_drone(processor_id, drone_id, drone_location, goal)
    return processor_dict[processor_id]["drones"][drone_id]["steps"]


def create_area():
    """Creates an area for the new processor
    Returns:
        matrix: area matrix that has obstacles"""
    matrix = np.zeros([4,50,50])
    no_go_areas = []
    while len(no_go_areas) < 20:
        rand = np.random.randint(0, 50, size=2)
        add_flag = 1
        if no_go_areas:
            for area in no_go_areas:
                if np.sqrt((rand[0] - area[0])**2 + (rand[1] - area[1])**2) < 5:
                    add_flag = 0
            if add_flag:
                no_go_areas.append(rand)
            add_flag = 1
        else:
            no_go_areas.append(rand)
    matrix = create_obstacles(matrix, no_go_areas)
    return matrix


def create_obstacles(matrix, obstacle_list) -> List[List[List[int]]]:
    """Creates obstacles for the area.
    Args:
        matrix: area matrix
        obstacle_list: a list of the obstacles to be placed in a 3x3 area
    Returns:
        matrix: area matrix with obstacles"""
    for obstacle in obstacle_list:
        row, col = obstacle
        for height in range(0, 4):
            for i in range(row, row+1):
                for j in range(col, col+1):
                    if i >= 0 and j >= 0 and i < 50 and j < 50:
                        matrix[height, i, j] = -1
    return matrix
        

def print_matrix_area(area: List[int], matrix) -> None:
    """Prints a specific area of the matrix, suitable for demoing movement.
    Args:
        area: A list containing the height, row and column of the object wanted to show
        matrix: the matrix where the object resides"""
    height, row, col = area
    row_mod = 5
    col_mod = 5
    if abs(row - 5) < 5:
        row_mod = abs(row - 5)
    if abs(col - 5) < 5:
        col_mod = abs(col - 5)
    rower = row-row_mod
    coler = col-col_mod
    while rower < 0:
        rower += 1
    while coler < 0:
        coler += 1
    print_matrix = matrix[height, rower:row+5, coler:col+5]
    print(print_matrix, file=sys.stderr, flush=True)
    time.sleep(1)


def process_processor(processor):
    for drone_num in processor['drones']:
        if not processor['drones'][drone_num]['moving']:
            get_drone_steps(processor['drones'][drone_num], processor['area'])
    

def get_rand_point(area):
    """Randomize a goal position for a drone."""
    while True:
        rand_row, rand_col = np.random.randint(0, 50, size=2)
        rand_height = np.random.randint(0, 4)
        if area[rand_height, rand_row, rand_col] == 0:
            return [rand_height, rand_row, rand_col]


def get_drone_steps(loc, goal, area):
    return astar(area, tuple(loc), tuple(goal))[1:]
    

def heuristic(node, goal):
    return ((node[0] - goal[0])**2 + (node[1] - goal[1])**2 + (node[2] - goal[2])**2)**0.5


def astar(matrix, start, goal):
    movements = [(0, 0, -1), (0, 0, 1), (0, -1, 0), (0, 1, 0), (-1, 0, 0), (1, 0, 0)]
    heap = []
    old = []
    heapq.heappush(heap, (heuristic(start, goal), start))
    costs = {start: 0}
    parents = {start: None}
    
    while heap:
        current = heapq.heappop(heap)[1]
        old.append(current)
        if current == goal:
            path = []
            while current:
                path.append(current)
                current = parents[current]
            return path[::-1]
        for move in movements:
            neighbor = (current[0] + move[0], current[1] + move[1], current[2] + move[2])
            if 0 <= neighbor[0] < len(matrix) and 0 <= neighbor[1] < len(matrix[0]) and 0 <= neighbor[2] < len(matrix[0][0]):
                cost = costs[current] + matrix[neighbor[0]][neighbor[1]][neighbor[2]]
                if (neighbor not in costs or cost < costs[neighbor]) and neighbor not in old:
                    costs[neighbor] = cost
                    priority = cost + heuristic(neighbor, goal)
                    parents[neighbor] = current
                    heapq.heappush(heap, (priority, neighbor))
    return None




def add_new_processor(processor_id, processor_area, processor_spawn):
    """Add new row into processor database"""
    global conn
    time.sleep(5)
    if conn == None:
        conn = psycopg2.connect(
        host="localhost",
        port=5432,
        database="HADES_db",
        user='HADES_main',
        password='notsecret')
    cur = conn.cursor()
    cur.execute("INSERT INTO processors (id, area, spawn) VALUES (%s, %s, %s)", (processor_id, pickle.dumps(processor_area), pickle.dumps(processor_spawn)))
    conn.commit()
    cur.close()
    print(f"Processor {processor_id} added to database", file=sys.stderr, flush=True)

def add_new_drone(processor_id, drone_id, drone_loc, drone_goal):
    """Add new drone into drone database"""    
    cur = conn.cursor()
    cur.execute("INSERT INTO drones (processor_id, drone_id, drone_loc, drone_goal) VALUES (%s, %s, %s, %s)", (processor_id, drone_id,  pickle.dumps(drone_loc), pickle.dumps(drone_goal)))
    conn.commit()
    cur.close()
    print(f"Drone {drone_id} for processor {processor_id} added to database", file=sys.stderr, flush=True)

def get_processor_info_by_id(processor_id):    
    cur = conn.cursor()
    cur.execute("SELECT * FROM processors WHERE id == %s", (processor_id))
    result = cur.fetchall()
    cur.close()
    
    for i, item in result:
        result[i] = [result[i][0], pickle.loads(result[i][1]), pickle.loads(result[i][2])]
    
    print(result)
    return result

def get_drones_by_processor_id(processor_id):    
    cur = conn.cursor()
    cur.execute("SELECT * FROM drones WHERE processor_id == %s", (processor_id))
    result = cur.fetchall()
    cur.close()
    
    for i, item in result:
        result[i] = [result[i][0], result[i][1], pickle.loads(result[i][2]), pickle.loads(result[i][3])]
    
    print(result)
    return result

def get_processors():
    cur = conn.cursor()
    cur.execute("SELECT * FROM processors")
    result = cur.fetchall()
    cur.close()
    
    for i, item in result:
        result[i] = [result[i][0], pickle.loads(result[i][1]), pickle.loads(result[i][2])]
    
    print(result)
    return result
