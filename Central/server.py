from flask import Flask
import numpy as np
import math
import heapq
import sys
import time
import http
import json

from typing import List

app = Flask(__name__)

processor_dict = {}


def create_area():
    """Creates an area for the new processor
    Returns:
        matrix: area matrix that has obstacles"""
    matrix = np.zeros([4,50,50])
    no_go_areas = []
    while len(no_go_areas) < 5:
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
    print_matrix = matrix[height, row-row_mod:row+5, col-col_mod:col+5]
    print(print_matrix, file=sys.stderr, flush=True)


def connect_processor():
    """Connects a new processor to the server and creates all necessary information to be processed"""
    if processor_dict:
        pass
    else:
        create_demo_processor()
        process_processor(processor_dict[0])


def process_processor(processor):
    for drone_num in processor['drones']:
        if not processor['drones'][drone_num]['moving']:
            get_drone_steps(processor['drones'][drone_num], processor['area'])


def create_demo_processor():
    """Creates a demo processor to be used for demoing purposes."""
    print("Demo mode", file=sys.stderr, flush=True)
    area = create_area()
    processor_dict[0] = {
        'area': area,
        'spawn': get_rand_point(area),
        'drones': {
            0: {
                'location': get_rand_point(area),
                'goal': get_rand_point(area),
                'moving': False,
                'steps': []
            }
        }
    }
    processor_dict[0]['spawn'][0] = 0 # sets spawn to ground point
    
    processor_dict[1] = {
        'address': "localhost:8080",
        'area': area,
        'spawn': get_rand_point(area),
        'drones': {
            0: {
                'location': get_rand_point(area),
                'goal': get_rand_point(area),
                'moving': False,
                'steps': []
            }
        }
    }
    
    conn = http.client.HTTPConnection('localhost:8080')
    conn.request("GET", "/drones")
    response = conn.getresponse()
    
    json.loads(bytes('[{"id": 0, "location": [34, 33, 49], "steps": [], "moving": false}, {"id": 1, "location": [17, 40, 12], "steps": [], "moving": false}, {"id": 2, "location": [11, 20, 26], "steps": [], "moving": false}, {"id": 3, "location": [44, 3, 43], "steps": [], "moving": false}, {"id": 4, "location": [6, 35, 43], "steps": [], "moving": false}, {"id": 5, "location": [10, 2, 28], "steps": [], "moving": false}]', "utf-8"));
    print(bytes('[{"id": 0, "location": [34, 33, 49], "steps": [], "moving": false}, {"id": 1, "location": [17, 40, 12], "steps": [], "moving": false}, {"id": 2, "location": [11, 20, 26], "steps": [], "moving": false}, {"id": 3, "location": [44, 3, 43], "steps": [], "moving": false}, {"id": 4, "location": [6, 35, 43], "steps": [], "moving": false}, {"id": 5, "location": [10, 2, 28], "steps": [], "moving": false}]', "utf-8"), file=sys.stderr, flush=True)
    i = 1
    print(response.read(), file=sys.stderr, flush=True)
    responsejson = json.loads(response.read())
    
    for drone in responsejson:
        processor_dict[1]['drones'][i] = {'location': drone["location"], 'moving': drone["moving"], 'steps': drone["steps"], 'goal': get_rand_point(area)}
        i += 1
    
    print(processor_dict[1]['drones'], file=sys.stderr, flush=True)
    """processor_dict[2] = {
        'address': "localhost:8081",
        'area': area,
        'spawn': get_rand_point(area),
        'drones': {
            0: {
                'location': get_rand_point(area),
                'goal': get_rand_point(area),
                'moving': False,
                'steps': []
            }
        }
    }
    """
    

def get_rand_point(area):
    """Randomize a goal position for a drone."""
    while True:
        rand_row, rand_col = np.random.randint(0, 50, size=2)
        rand_height = np.random.randint(0, 4)
        if area[rand_height, rand_row, rand_col] == 0:
            return [rand_height, rand_row, rand_col]


def get_drone_steps(drone_dict, area):
    drone_dict['moving'] = True
    loc = drone_dict['location']
    goal = drone_dict['goal']
    steps = astar(area, tuple(loc), tuple(goal))
    for i, step in enumerate(steps):
        steps[i] = np.array(step)
    drone_dict['steps'] = steps
    print(drone_dict, file=sys.stderr, flush=True)
    
    # send steps through HTTP
    

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


print("waiting for processors", file=sys.stderr, flush=True)
time.sleep(4)
connect_processor()



@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

if __name__ == "__main__":
    connect_processor()
