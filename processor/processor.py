import requests as req
import time
import random
import json
import sys

own_port = 5000
main_server_url = "http://localhost:8080"

self_id = 500

drones = []

def main():
    wait_time = 5
    connected = False
    create_drones()
    while True:
        if not connected:
            try:
                conn = req.get(main_server_url+"/connect")
                if conn.status_code == 200:
                    self_id = int(conn.content)
                    connected = True
            except req.ConnectionError:
                main_server_down()
        else:
            get_drone_steps()
            for drone in drones:
                if drone["steps"] and drone["moving"] == False:
                    move_drone(drone)


def move_drone(drone):
    """Move drone one step and send a step confirm to main server
    Args: 
        drone: drone information"""
    print("Not done yet, putting in input here so you can break out of this loop", file=sys.stderr, flush=True)
    input()


def get_drone_steps():
    for drone in drones:
        if drone["steps"] == []:
            try:
                drone_steps = req.post(main_server_url+"/add_drone", json={"id": self_id, "drone": drone})
                drone["steps"] = json.loads(drone_steps.content.decode("utf8"))
            except req.ConnectionError:
                main_server_down()


def create_drones():
    for i in range(0,6):
        drones.append({'id': i, 'location': [random.randint(0, 4), random.randint(0, 50), random.randint(0, 50)], 'steps': [], 'moving': False})


def main_server_down():
    wait_time = 10
    print(f"Main server not on, waiting for {wait_time}", file=sys.stderr, flush=True)
    time.sleep(wait_time)


if __name__ == "__main__":
    main()
