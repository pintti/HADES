import requests as req
import time
import random
import json
import sys

own_port = 5000
main_server_url = "http://localhost:8080"

SelfId = 500

drones = []

def main():
    connected = False
    global SelfId
    create_drones()
    while True:
        if not connected:
            try:
                conn = req.get(main_server_url+"/connect")
                if conn.status_code == 200: 
                    SelfId= int(conn.content)
                    connected = True
            except req.ConnectionError:
                main_server_down()
        else:
            get_drone_steps()
            for drone in drones:
                if drone["steps"]:
                    move_drone(drone)


def move_drone(drone):
    """Move drone one step and send a step confirm to main server
    Args: 
        drone: drone information"""
    step = drone["steps"].pop(0)
    drone_id = drone["id"]
    print(f"Drone {drone_id} moving to {step}", file=sys.stderr, flush=True)
    req.post(main_server_url+"/drone", json={"id": SelfId, "drone_id": drone_id, "drone_loc": step})
    time.sleep(1)


def get_drone_steps():
    for drone in drones:
        drone_id = drone["id"]
        if drone["steps"] == [] and drone["moving"] is False:
            try:
                print(f"Getting movement for drone {drone_id}.", file=sys.stderr, flush=True)
                drone_steps = req.post(main_server_url+"/add_drone", json={"id": SelfId, "drone": drone})
                drone["steps"] = json.loads(drone_steps.content.decode("utf8"))
            except req.ConnectionError:
                main_server_down()
        elif drone["steps"] == []:
            print(f"Drone {drone_id} has finished movement.", file=sys.stderr, flush=True)
            time.sleep(3)
            drone["moving"] = False
        else:
            drone["moving"] = True


def create_drones():
    for i in range(1,7):
        drones.append({'id': i, 'location': [random.randint(0, 3), random.randint(0, 49), random.randint(0, 49)], 'steps': [], 'moving': False})


def main_server_down():
    wait_time = 5
    print(f"Main server not on, waiting for {wait_time}", file=sys.stderr, flush=True)
    time.sleep(wait_time)


if __name__ == "__main__":
    main()
