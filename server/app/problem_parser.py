
import functools

from planner import AtomicSentence
from planner import State
from planner import Action
from planner import Variable

def unload_partial(obj_attribute, world_objects):
    """ 
        Given Variable instance and object attribute, 
        find the one which is a CAR object,
        and compute UNLOAD action impact value 
    """

    car_objects = [w_o for w_o in world_objects if w_o.type=="CAR"]
    world_obj = None
    if len(car_objects)>0:
        world_obj = car_objects[0]
    
    action_impact = 0

    if world_obj is not None:
        action_impact = -1*world_obj.attributes[obj_attribute]
    
    return action_impact
    

def load_partial(obj_attribute, world_objects):
    """
        Given Variable instance and object attribute,
        find the one which is a CAR object,
        and compute LOAD action impact value
    """
    
    car_objects = [w_o for w_o in world_objects if w_o.type=="CAR"]
    
    world_obj = None
    if len(car_objects)>0:
        world_obj = car_objects[0]
    
    action_impact = 0

    if world_obj is not None:
        action_impact = -1*world_obj.attributes[obj_attribute]
    
    return action_impact

class ProblemParser:
    """
        The function of this class is to read the planning problem specified in 
        the provided JSON document, and produce the resulting initial state and goal statements. 
    """
    
    def __init__(self, problem_as_dict):
        self.problem_dict = problem_as_dict
        self.parse_problem()
    
    def parse_problem(self):
        
        #Obtain objects
        self.objects = self.get_problem_objects()

        #Obtain init state
        self.init_state = self.get_init_state()

        #Get actions from domain
        self.actions = self.get_domain_actions()

        self.goal = None
    
    def get_problem_objects(self):
        
        objects = []
        
        #The World
        the_world = Variable("world", "domain", "The World", attributes={"number-trips":0})

        #People
        #---------------------------
        people = []

        people_data = self.problem_dict["persons"]

        person_index = 0
        for person in people_data:
            person_var = Variable("person_%s" % person_index, "person", person["name"], attributes={"trips-taken":0, "home":person["home"]})
            people.append(person_var)
            person_index+=1
        #---------------------------
        
        locations = []

        location_strings = [] 
        location_strings.extend([l["location"] for l in self.problem_dict["locations"]])
        location_strings.extend( [p["home"] for p in self.problem_dict["persons"]] )
        
        loc_index = 0
        for loc_str in location_strings:
            loc_var = Variable("location_%s" % loc_index, "location", loc_str, attributes={"supply":0, "demand":0}) 
            locations.append(loc_var)
            loc_index+=1
        #---------------

        cars = []

        car_index = 0
        for c in self.problem_dict["cars"]:
            car_var = Variable("car_%s" % car_index, "car", c["name"], attributes={"capacity":c["capacity"], "owner":c["owner"]})
            cars.append(car_var)
            car_index+=1
        
        objects = people
        objects.extend(locations)
        objects.extend(cars)
        objects.append(the_world)

        return objects
    
    def get_init_state(self):
        """ 
            Assumes that car initial locations are same as owner.
        """
        
        #People locations
        #-------------------
        people_locations = []
        people_data = self.problem_dict["persons"]
        for person in people_data:
            person_var = Variable("person-x", "PERSON", person["name"], attributes={"trips-taken":0, "home":person["home"]})
            home_location_var = Variable("location-x", "LOCATION", person["home"])
            new_person_loc = AtomicSentence("at", [home_location_var, person_var])
            people_locations.append(new_person_loc)
        #-------------------

        #Car locations
        #--------------
        car_locations = []
        car_data = self.problem_dict["cars"]
        car_index = 0
        for c in car_data:
            car_var = Variable("car_%s" % car_index, "car", c["name"], attributes={"capacity":c["capacity"], "owner":c["owner"]})
            
            #Find Car's owner's home location
            #--------------------------------
            target_atom_sent = None
            for p_l in people_locations:
                people_matching_owner = [t for t in p_l.terms if t.bound_val==c["owner"]]
                if len(people_matching_owner)>0:
                    target_atom_sent = p_l
                    break
            
            car_loc_var = None
            if target_atom_sent is not None:
                car_loc_var = [t for t in target_atom_sent.terms if t.type=="LOCATION"][0]
            #--------------------------------

            #Assert new AtomicSentence
            new_car_loc_as = AtomicSentence("at", [car_loc_var, car_var])

            car_locations.append(new_car_loc_as)

            car_index+=1
        #--------------

        initial_state_val = people_locations
        initial_state_val.extend(car_locations)

        init_state = State(initial_state_val)

        #Initial metric values

        #------------------
        
        #The world - number-trips
        init_state.metrics["The World"] = {}
        init_state.metrics["The World"]["number-trips"] = 0

        #People - trips-taken
        for p in people_data:
            init_state.metrics[p["name"]] = {}
            init_state.metrics[p["name"]]["trips-taken"] = 0
        
        #Locations - supply and demand
        #-----------------------------
        for loc in self.problem_dict["locations"]:
            loc_supply = 0
            loc_demand = 0
            if "supply" in loc:
                loc_supply = loc["supply"]
            
            if "demand" in loc:
                loc_demand = loc["demand"]
            
            init_state.metrics[loc["location"]] = {}
            init_state.metrics[loc["location"]]["supply"] = loc_supply 
            init_state.metrics[loc["location"]]["demand"] = loc_demand

        #Also initialize locations appearing in peoples' home locations
        home_loc_strings = []
        home_loc_strings.extend( [p["home"] for p in self.problem_dict["persons"]])

        for loc_string in home_loc_strings:
            init_state.metrics[loc_string] = {}
            init_state.metrics[loc_string]["supply"] = 0
            init_state.metrics[loc_string]["demand"] = 0
        #-----------------------------


        for c in self.problem_dict["cars"]:
            car_capacity = 50
            if "capacity" in c:
                car_capacity = c["capacity"]
            
            init_state.metrics[c["name"]] = {}
            init_state.metrics[c["name"]]["capacity"] = car_capacity

        return init_state
    
    def get_domain_actions(self):
        actions = []
        
        #Drive
        #----------------------------------------
        world = Variable("world", "domain", attributes={"number-trips":0})
        person_a = Variable("person_a", "person", attributes={"trips-taken":0})
        loc_from = Variable("from_loc", "location", attributes={"supply":0, "demand":0})
        loc_to = Variable("to_loc", "location", attributes={"supply":0, "demand":0})
        car_a = Variable("car_a", "car")

        args_drive = [person_a, car_a, loc_from, loc_to, world]
        drive_precons = {"positive":[AtomicSentence("at", [car_a, loc_from] ), AtomicSentence("assigned", [person_a, car_a])], "negative":[], "metrics":[] }
        drive_effects = {"add":[AtomicSentence("at", [car_a, loc_to])], "delete":[AtomicSentence("at", [car_a, loc_from])],
                            "metrics":[{"object":world, "attribute":"number-trips", "impact":1}, 
                                        {"object":person_a, "attribute":"trips-taken", "impact":1}] }

        drive_action = Action("Drive", args_drive, drive_precons, drive_effects)
        #----------------------------------------

        actions.append(drive_action)
        
        #Load
        #---------------------------------------- 
        world = Variable("world", "domain", attributes={"number-trips":0})
        
        car_a = Variable("car_a", "car", attributes={"capacity":200})
        loc_a = Variable("loc_a", "location", attributes={"supply":0, "demand":0})
        args_load = [car_a, loc_a, world]
        load_precons = {"positive":[AtomicSentence("at", [car_a, loc_a])], "negative":[AtomicSentence("carrying-load", [car_a])],
                            "metrics":[
                                    {"object":loc_a, "attribute":"supply", "operation":"gt", "value":0}
                                ] 
                        }
        load_effects = {"add":[AtomicSentence("carrying-load", [car_a])], "delete":[], 
                            "metrics":[
                                {"object":loc_a, "attribute":"supply", "impact":functools.partial(load_partial, "capacity")}
                                ] 
                        }
        load_action = Action("Load", args_load, load_precons, load_effects)
        #----------------------------------------

        actions.append(load_action)
        

        world = Variable("world", "domain", attributes={"number-trips":0})
        
        car_a = Variable("car_a", "car", attributes={"capacity":200})
        loc_a = Variable("loc_a", "location", attributes={"supply":0, "demand":0})
        args_unload = [car_a, loc_a, world]
        
        unload_precons = {"positive":[AtomicSentence("carrying-load", [car_a]), AtomicSentence("at", [car_a, loc_a])], "negative":[], 
                    "metrics":[ {"object":loc_a, "attribute":"demand", "operation":"gt", "value":0} ]
                    }
        unload_effects = {"add":[], "delete":[AtomicSentence("carrying-load", [car_a])], 
                    "metrics":[{"object":loc_a, "attribute":"demand", "impact":functools.partial(unload_partial, "capacity")}
        ]}

        unload_action = Action("Unload", args_unload, unload_precons, unload_effects)
        #bound_unload = get_bound_actions(unload_action, world_objects)
        #----------------------------------------

        actions.append(unload_action)
        
        world = Variable("world", "domain", attributes={"number-trips":0})

        car_a = Variable("car_a", "car", attributes={"capacity":200})
        loc_a = Variable("loc_a", "location", attributes={"supply":0, "demand":0})
        person_a = Variable("person_a", "person", attributes={"trips-taken":0})
        
        args_assign = [person_a, car_a, loc_a, world]
        assign_precons = {"positive":[AtomicSentence("at", [car_a, loc_a]), AtomicSentence("at", [person_a, loc_a])], "negative":[AtomicSentence("is-assigned", [person_a])], "metrics":[]} 
        assign_effects = {"add":[AtomicSentence("assigned", [person_a, car_a]), AtomicSentence("is-assigned", [person_a])], "delete":[AtomicSentence("at", [person_a, loc_a])], "metrics":[]}
        
        assign_action = Action("Assign", args_assign, assign_precons, assign_effects)
        
        #----------------------------------------

        actions.append(assign_action)

        return actions
    
