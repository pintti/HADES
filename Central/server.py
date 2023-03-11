from flask import Flask
import numpy as np
from typing import List

app = Flask(__name__)

processor_dict = {}


def create_area():
    matrix = np.zeros([4,50,50])
    no_go_areas = []
    while len(no_go_areas) < 6:
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
    spawn_point = no_go_areas.pop(-1)
    matrix = create_obstacles(matrix, no_go_areas)
    return matrix, spawn_point


def create_obstacles(matrix, obstacle_list) -> List[List[List[int]]]:
    for obstacle in obstacle_list:
        row, col = obstacle
        for height in range(0, 4):
            for i in range(row-1, row+2):
                for j in range(col-1, col+2):
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
    print(print_matrix)


def connect_processor():
    """Connects a new processor to the server and creates all necessary information to be processed"""
    if processor_dict:
        pass
    else:
        create_demo_processor()


def process_processors():
    pass
    

def create_demo_processor():
    print("Demo mode")
    area, spawn_point = create_area()
    processor_dict[0] = {
        'area': area,
        'spawn': spawn_point,
        'drones': {
            0: create_demo_drone(spawn_point)
        }
    }
    print(processor_dict)


def create_demo_drone(spawn_point: List[int]):
    location = [0, spawn_point[0], spawn_point[1]]
    goal = [0, 0, 0]
    return {"location": location, 'goal': goal}


if __name__ == "__main__":
    connect_processor()
