from flask import Flask, request
import random
import json

app = Flask(__name__)

processorid = 0
drones = []


@app.before_first_request
def create_random_drones():
    # create random drones
    for i in range(0,6):
        drones.append({'id': i, 'location': [random.randint(0, 50), random.randint(0, 50), random.randint(0, 50)], 'steps': [], 'moving': False})

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

@app.route("/setid/<int:newid>")
def setid(newid):
    """
    Central can use this to set the id for this processor
    """
    processorid = newid
    return "OK", 200

@app.route("/drones")
def get_drones_list():
    """
    get list of all drones
    """
    drones_list = []
    for drone in drones:
        drones_list.append(drone)
    return json.dumps(drones_list), 200

@app.route("/drones/<int:droneid>", methods=["GET", "POST"])
def drone(droneid):
    """
    GET: get current status of drone
    POST: 
    """
    if request.method == "GET":
        for drone in drones:
            if drone['id'] == droneid:
                return json.dumps(drone), 200
        return "drone not found", 418
    #elif request.method == "POST":
        
