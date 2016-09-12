
import hashlib
import datetime

from app import app
from flask import request

from plan_interface import PlannerManager
from plan_option_generator import PlanOptionGenerator


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


@app.route("/session", methods=["PUT"])
def create_session():
    
    #Generate session hash
    #---------------------
    current_time = datetime.datetime.now()
    requester_ip = request.remote_addr
    
    session_hash = get_session_hash(current_time, requester_ip)
    #---------------------

    #Store session data in DB
    #------------------------

    #------------------------

    json_data = {"session_id":session_hash}

    return str(json_data)

@app.route("/planselection", methods=["PUT"])
def choose_plan():
    
    #Retrieve selection

    #

@app.route("/planoptions", methods=["PUT"])
def get_plan_options():
    data_as_dict = request.get_json()

    session_id = data_as_dict["session_id"]
    
    option_generator = PlanOptionGenerator(data_as_dict)
    
    #Store options in DB
    #-------------------
    
    #-------------------
    
    response_data = option_generator.execute()

    return str(response_data)


@app.route("/plan", methods=["POST", "PUT"])
def get_plan():
    
    data_as_dict = request.get_json()
    
    instance = PlannerManager(data_as_dict)
    
    #This will hang until planner is complete. 
    response_data = instance.execute()

    return str(response_data)
