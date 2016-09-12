
from app import app
from flask import request

import plan_interface
import hashlib
import datetime

@app.route('/')
@app.route('/index')
def index():
    return "Hello, World!"

@app.route('/echo', methods=["POST", "PUT"])
def echo_payload():
    json_data = request.get_json()
    print "JSON Payload: %s" % json_data
    
    return str(json_data)

def get_session_hash(current_time, requester_ip):
    md5 = hashlib.md5()
    md5.update(str(current_time))
    md5.update(str(requester_ip))

    return md5.hexdigest()


@app.route("/createsession", methods=["PUT"])
def create_session():
    
    #Generate session hash
    #---------------------
    current_time = datetime.datetime.now()
    requester_ip = request.remote_addr
    
    session_hash = get_session_hash(current_time, requester_ip)
    #---------------------

    json_data = {"session_id":session_hash}

    return str(json_data)

@app.route("/chooseplan", methods=["PUT"])
def choose_plan():
    pass

@app.route("/plan", methods=["POST", "PUT"])
def get_plan():
    
    data_as_dict = request.get_json()
    
    instance = plan_interface.PlannerManager(data_as_dict)
    
    #This will hang until planner is complete. 
    response_data = instance.execute()

    return str(response_data)
