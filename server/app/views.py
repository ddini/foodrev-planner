
from app import app
from flask import request

import plan_interface

@app.route('/')
@app.route('/index')
def index():
    return "Hello, World!"

@app.route('/echo', methods=["POST", "PUT"])
def echo_payload():
    json_data = request.get_json()
    print "JSON Payload: %s" % json_data
    
    return str(json_data)

@app.route("/plan", methods=["POST", "PUT"])
def get_plan():
    
    data_as_dict = request.get_json()
    
    instance = plan_interface.PlannerManager(data_as_dict)
    
    #This will hang until planner is complete. 
    response_data = instance.execute()

    return str(response_data)
