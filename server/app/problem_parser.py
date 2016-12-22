
import functools

from planner import AtomicSentence
from planner import State
from planner import Action
from planner import Variable

# class AtomicSentence():
    
#     def __init__(self, name, terms):
#         self.name = name
#         self.terms = terms
    
#     def __str__(self):
#         return_str = "%(name)s (" % {"name":self.name}
        
#         return_str+=", ".join([str(t) for t in self.terms])
                
#         return_str+=")"
#         return return_str
    
#     def __eq__(self, other):
#         return_val = True
        
#         #names are equal
#         if self.name != other.name:
#             return False

#         #same number of terms
#         if len(self.terms) != len(other.terms):
#             return False

#         #For each term, there exists a term in other s.t. they are equal
#         for t in self.terms:
#             if not t in other.terms:
#                 return_val = False
#                 break

#         return return_val 

#     def bind(self, **bindings):
#         pass

# class State():

#     def __init__(self, value):
#         self.value = value
#         self.prev_state = None
#         self.prev_action = None
#         self.metrics = {}
    
#     def enumerate_plan(self):

#         acc_list = []

#         curr_node = self
#         while curr_node.prev_state is not None:
#             acc_list.append(curr_node.prev_action)
#             curr_node = curr_node.prev_state

#         return acc_list
    
#     def h(self):
#         outstanding_demand = 0

#         for k in self.metrics:
#             if "demand" in self.metrics[k]:
#                 outstanding_demand+=self.metrics[k]["demand"]
        
#         outstanding_supply = 0

#         for k in self.metrics:
#             if "supply" in self.metrics[k]:
#                 outstanding_supply+=self.metrics[k]["supply"]
        
#         total_num_trips = self.metrics["The World"]["number-trips"]
#         return (outstanding_supply*outstanding_supply + outstanding_demand*outstanding_demand +total_num_trips*total_num_trips)
    
#     def __str__(self):
#         return "state: %s h:%s" % (str(self.value), str(self.h()))

# class Variable():
#     def __init__(self, name, var_type=None, value=None, attributes=None):
#         self.name = name
#         self.type = var_type.upper()
#         self.bound_val = value
#         self.attributes = attributes
    
#     def __str__(self):
#         return_str = "%(name)s : %(var_type)s - %(b_val)s" % {"name":self.name, "var_type":self.type.upper(), "b_val":self.bound_val}
        
#         return return_str
    
#     def __eq__(self, other):
#         return (self.type == other.type) and (self.bound_val == other.bound_val)

# class Action():

#     def __init__(self, name, terms, preconditions, effects):
#         """ 'terms' is a list of (unbound) variables """
        
#         self.name = name
#         self.terms = terms

#         #List of AtomicSentence instances
#         self.preconditions = preconditions
        
#         #Dictionary of two lists, keyed as "add" and "delete", each of AtomicSentence instances
#         self.effects = effects
    
#     def bind(self, **term_bindings):

#         #Bind terms in term list
#         for t in self.terms:
#             term_name = t.name
#             if term_name in term_bindings:
#                 bound_term = term_bindings[term_name]
#                 t.bound_val = bound_term.bound_val
#                 t.attributes = bound_term.attributes
    
#     def __str__(self):
#         return_str = "Action: %(name)s (" % {"name":self.name}
#         # for t in self.terms:
#         #     return_str+="%(term_name)s:%(term_type)s:%(term_val)s " % {"term_name":t.name, "term_type":t.type.upper(), "term_val":t.bound_val}
        
#         return_str+=", ".join([str(t) for t in self.terms])
#         return_str+=")"
    
        
#         return return_str

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
        # people = [Variable("person_a", "person", "Greg & David", attributes={"trips-taken":0, "home":person_1_home}),
        #     Variable("person_b", "person", "Kenny & Maria", attributes={"trips-taken":0, "home":person_2_home}), 
        #     Variable("person_c", "person", "Rona & David", attributes={"trips-taken":0, "home":person_3_home}),
        #     Variable("person_d", "person", "Leesa", attributes={"trips-taken":0, "home":person_4_home}),
        #     Variable("person_e", "person", "Cassandra", attributes={"trips-taken":0, "home":person_5_home})
        #     ]

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
        
        #Locations
        #---------------
        # source_loc_1 = "1919 22nd Street, San Francisco, CA 94107"
        # source_loc_2 = "mission st and cesar chavez st., San Francisco, CA 94110"

        # dest_loc_1 = "65 9th Street, San Francisco, CA"
        # dest_loc_2 = "668 Clay St, San Francisco, CA"

        # person_1_home = "289 Hamilton Street, San Francisco, CA 94134"
        # person_2_home = "289 Hamilton Street, San Francisco, CA 94134"
        # person_3_home = "Palo Alto, CA"
        # person_4_home = "Brisbane, CA"
        # person_5_home = "Brisbane, CA"


        # locations = [Variable("location_1", "location", source_loc_1, attributes={"supply":700, "demand":0}),
        #     Variable("location_2", "location", source_loc_2, attributes={"supply":1150, "demand":0}), 
        #     Variable("location_3", "location", dest_loc_1, attributes={"supply":0, "demand":800}),
        #     Variable("location_4", "location", dest_loc_2, attributes={"supply":0, "demand":1050}),
        #     Variable("location_5", "location", person_1_home, attributes={"supply":0, "demand":0}),
        #     Variable("location_6", "location", person_2_home, attributes={"supply":0, "demand":0}),
        #     Variable("location_7", "location", person_3_home, attributes={"supply":0, "demand":0}),
        #     Variable("location_8", "location", person_4_home, attributes={"supply":0, "demand":0}),
        #     Variable("location_9", "location", person_5_home, attributes={"supply":0, "demand":0})]
        
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


        #Cars
        # cars = [Variable("car_1", "car", "Greg & David car'", attributes={"capacity":200}),
        #         Variable("car_2", "car", "Kenny & Maria car", attributes={"capacity":200}),
        #         Variable("car_3", "car", "Rona & David car", attributes={"capacity":350}),
        #         Variable("car_4", "car", "Leesa car", attributes={"capacity":200}),
        #         Variable("car_5", "car", "Cassandra car", attributes={"capacity":200})]

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
    
