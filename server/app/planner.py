import itertools

from copy import deepcopy
from Queue import PriorityQueue
import math
import random
import logging
import functools

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)

class WorldObject():
    def __init__(self, name, object_type=None):
        self.name=name
        self.type = object_type
    
    def __str__(self):
        return "Object: %(name)s - %(type)s" % {"name":self.name, "type":self.type} 

class AtomicSentence():
    
    def __init__(self, name, terms):
        self.name = name
        self.terms = terms
    
    def __str__(self):
        return_str = "%(name)s (" % {"name":self.name}
        
        return_str+=", ".join([str(t) for t in self.terms])
                
        return_str+=")"
        return return_str
    
    def __eq__(self, other):
        return_val = True
        
        #names are equal
        if self.name != other.name:
            return False

        #same number of terms
        if len(self.terms) != len(other.terms):
            return False

        #For each term, there exists a term in other s.t. they are equal
        for t in self.terms:
            if not t in other.terms:
                return_val = False
                break

        return return_val 

    def bind(self, **bindings):
        pass

class State():

    def __init__(self, value):
        self.value = value
        self.prev_state = None
        self.prev_action = None
        self.metrics = {}
    
    def enumerate_plan(self):

        acc_list = []

        curr_node = self
        while curr_node.prev_state is not None:
            acc_list.append(curr_node.prev_action)
            curr_node = curr_node.prev_state

        return acc_list
    
    def h(self):
        outstanding_demand = 0

        for k in self.metrics:
            if "demand" in self.metrics[k]:
                outstanding_demand+=self.metrics[k]["demand"]
        
        outstanding_supply = 0

        for k in self.metrics:
            if "supply" in self.metrics[k]:
                outstanding_supply+=self.metrics[k]["supply"]
        
        total_num_trips = self.metrics["The World"]["number-trips"]
        return (outstanding_supply*outstanding_supply + outstanding_demand*outstanding_demand +total_num_trips*total_num_trips)
    
    def __str__(self):
        return "state: %s h:%s" % (str(self.value), str(self.h()))

class Variable():
    def __init__(self, name, var_type=None, value=None, attributes=None):
        self.name = name
        self.type = var_type.upper()
        self.bound_val = value
        self.attributes = attributes
    
    def __str__(self):
        return_str = "%(name)s : %(var_type)s - %(b_val)s" % {"name":self.name, "var_type":self.type.upper(), "b_val":self.bound_val}
        
        return return_str
    
    def __eq__(self, other):
        return (self.type == other.type) and (self.bound_val == other.bound_val)

class Action():

    def __init__(self, name, terms, preconditions, effects):
        """ 'terms' is a list of (unbound) variables """
        
        self.name = name
        self.terms = terms

        #List of AtomicSentence instances
        self.preconditions = preconditions
        
        #Dictionary of three lists, keyed as "add", "delete", and "metrics". First two are of AtomicSentence instances
        #Last is list of dictionaries, of the following format:
        #
        #   "object":<Variable instance>
        #   "attribute":<string value>
        #   "impact":<float>
        self.effects = effects
    
    def bind(self, **term_bindings):

        #Bind terms in term list
        for t in self.terms:
            term_name = t.name
            if term_name in term_bindings:
                bound_term = term_bindings[term_name]
                t.bound_val = bound_term.bound_val
                t.attributes = bound_term.attributes
        
        #Change metric effect values
        for m_e in self.effects["metrics"]:
            #Set value for 'impact', which may be a function
            #of bound terms, and so now may need to be re-evaluated.
            
            impact_is_partial = (type(m_e["impact"]) == functools.partial)

            if impact_is_partial:
                partial_func = m_e["impact"]
                m_e["impact"] = partial_func(self.terms)            
            # else - this value is already a number and no action need be taken.

        
    
    def __str__(self):
        return_str = "Action: %(name)s (" % {"name":self.name}
        # for t in self.terms:
        #     return_str+="%(term_name)s:%(term_type)s:%(term_val)s " % {"term_name":t.name, "term_type":t.type.upper(), "term_val":t.bound_val}
        
        return_str+=", ".join([str(t) for t in self.terms])
        return_str+=")"
    
        
        return return_str

class Planner():

    def __init__(self, actions, world_objects, init_state, goal):
        """ 
            'metrics' is an optional dictionary of metric values to keep track of and use
            in effects, preconditions, goals, and optimization statements during
            planning. 

            They values in the above dictionary takes two forms:
                -Global - just a named float to keep track of.
                -Functional - A dictionary, which keeps track of values for separate world objects.
        """
        
        self.state_pq = PriorityQueue()
        self.state_pq.put( (init_state.h(), init_state) )
        
        self.actions = actions
        self.goal = goal
        self.w_objects = world_objects

        #Action --> [bound_action, bound_action, ...]
        self.bound_acts_dict = {}
        self.all_bound_actions = []
        self.set_bound_actions()
    
    def get_object_combinations(self, variable_list):
        
        #Produce world objects of types relevant to
        #variable_list
        objects_by_type = []
        for v in variable_list:
            var_type = v.type
            objects_of_type = [w for w in self.w_objects if w.type==var_type]
            objects_by_type.append(objects_of_type)
        

        #Produce all valid combinations of objects
        element_iterator = itertools.product(*objects_by_type)
        combos = [e for e in element_iterator]

        return combos

    
    def get_bound_actions_for_unbound(self, unbound_act):
        logging.info("Call to get_bound_actions_for_unbound: %s", str(unbound_act) )

        bound_actions = []

        parameter_combinations = self.get_object_combinations(unbound_act.terms)

        for c in parameter_combinations:
            act_copy = deepcopy(unbound_act)
            bindings_dict = {}
            
            for var_index in range(len(c)):
                bound_parameter = c[var_index]
                term_param = act_copy.terms[var_index]
                #bindings_dict[term_param.name] = bound_parameter.bound_val
                bindings_dict[term_param.name] = bound_parameter

            act_copy.bind(**bindings_dict)
            
            bound_actions.append(act_copy)

        return bound_actions

    
    def set_bound_actions(self):
        logging.info("Call to get_bound_actions")

        for a in self.actions:
            bound_actions = self.get_bound_actions_for_unbound(a)
            self.bound_acts_dict[a] = bound_actions
        
        for k in self.bound_acts_dict:
            self.all_bound_actions.extend(self.bound_acts_dict[k])
    
    def goal_is_met(self, aState):
        return_val = False

        outstanding_demand = 0

        for k in aState.metrics:
            if "demand" in aState.metrics[k]:
                outstanding_demand+=aState.metrics[k]["demand"]
        
        if outstanding_demand==0:
            return_val = True

        return return_val
    
    def preconditions_are_met(self, bound_action, state_node):
        
        conditions_are_met = True

        #positive preconditions
        #----------------------
        positive_precons = bound_action.preconditions["positive"]

        state_AS_list = state_node.value
        for p in positive_precons:
            if not p in state_AS_list:
                conditions_are_met = False
                #print "VIOLATED due to positive precons."
                break
        #----------------------
        
        #negative preconditions
        #----------------------
        negative_precons = bound_action.preconditions["negative"]

        for n in negative_precons:
            if n in state_AS_list:
                conditions_are_met = False
                #print "VIOLATED due to negative precons."
                break
                
        #----------------------

        #Metric preconditions
        metric_precons = bound_action.preconditions["metrics"]

        # unload_precons = {"positive":[AtomicSentence("carrying-load", [car_a]), AtomicSentence("at", [car_a, loc_a])], "negative":[], 
        #         "metrics":[ {"object":loc_a, "attribute":"demand", "operation":"gt", "value":0} ]
        #         }

        for m in metric_precons:
            world_object = m["object"]

            #Retrieve object's current attribute value
            #-----------------------------------------
            object_name = world_object.bound_val
            attr_value = state_node.metrics[object_name][m["attribute"]]
            
            #print "object: %s" % object_name
            #print "attribute: %s value: %s" % (m["attribute"], attr_value)
            #-----------------------------------------
            
            #Determine operation and test value
            test_val = m["value"]

            #print "test value: %s" % test_val

            if m["operation"]=="gt":
                test_bool = attr_value > test_val
            elif m["operation"]=="gte":
                test_bool = attr_value>= test_val
            elif m["operation"]=="lt":
                test_bool = attr_value< test_val
            elif m["operation"]=="lte":
                test_bool = attr_value<= test_val
            else:
                test_bool = False
            
            if not test_bool:
                conditions_are_met = False
                #print "VIOLATED due to metric precons."
                break

        return conditions_are_met

    
    def act_on(self, bound_action, state_node):
        new_state_node = None

        new_state_node = deepcopy(state_node)

        #Delete effects
        #--------------
        delete_effects = bound_action.effects["delete"]

        items_to_remove = []
        for element in new_state_node.value:
            if element in delete_effects:
                items_to_remove.append(element)

        for i in items_to_remove:
            new_state_node.value.remove(i)
        #--------------

        #Add effects
        #------------
        add_effects = bound_action.effects["add"]
        new_state_node.value.extend(add_effects)
        #------------

        #Execute metrics adjustments
        #---------------------------
        metric_effects = bound_action.effects["metrics"]

        for m_e in metric_effects:
            #Identify receving of impact and 
            #type of impact
            impacted_object = m_e["object"]
            attribute = m_e["attribute"]
            impact_amount = m_e["impact"]

            new_state_node.metrics[impacted_object.bound_val][attribute]+=impact_amount

        #---------------------------

        return new_state_node
    
    def step(self, current_node, sample=10):
        
        valid_actions = [a for a in self.all_bound_actions if self.preconditions_are_met(a, current_node)]
        
        if sample is not None:
            #logging.info("Sampling action space.")
            sampled_actions = [random.choice(valid_actions) for x in range(sample)]
            for s_a in sampled_actions:
                new_state = self.act_on(s_a, current_node)

                new_state.prev_state = current_node
                new_state.prev_action = s_a

                self.state_pq.put((new_state.h(), new_state))
        else:
            for a in valid_actions:
                new_state = self.act_on(a, current_node)

                new_state.prev_state = current_node
                new_state.prev_action = a

                self.state_pq.put((new_state.h(), new_state))
                        
    
    def execute_iterate(self, num_iterations=10):
        current_node = self.state_pq.get()
        current_node = current_node[1]

        i = 0
        while (current_node is not None) and (i<num_iterations):
            
            if i%100 == 0:
                logging.info("iteration #: %s", i)
            
            self.step(current_node)

            if not self.state_pq.empty(): 
                current_node = self.state_pq.get()
                current_node = current_node[1]
            else:
                current_node = None
            
            i+=1

        return current_node
    
    def execute(self, plans_to_find=3, sample=None):
        
        plans = []

        current_node = self.state_pq.get()
        current_node = current_node[1]

        i = 0
        while (current_node is not None):
            if i%100 == 0:
                logging.info("iteration #: %s", i)
                logging.info("Current metrics: %s", current_node.metrics)
                logging.info("queue size: %s" % self.state_pq.qsize())
            
            if self.goal_is_met(current_node):
                logging.info("Found plan #: %s",len(plans) )
                plans.append(current_node)
            
            if len(plans)>=plans_to_find:
                break

            self.step(current_node)

            if not self.state_pq.empty(): 
                current_node = self.state_pq.get()
                current_node = current_node[1]
            else:
                current_node = None
            
            i+=1

        return_plans = None

        if sample:
            return_plans = [random.choice(plans) for x in range(sample)]
        else:
            return_plans = plans

        return return_plans

def effect_function(**args):
    """ Specified on a per domain basis """
    pass

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

def get_test_domain():
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
    #bound_drive = get_bound_actions(drive_action, world_objects)
    #----------------------------------------
    
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

    #Unload
    #----------------------------------------
    
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
    #----------------------------------------
    
    world = Variable("world", "domain", attributes={"number-trips":0})

    car_a = Variable("car_a", "car", attributes={"capacity":200})
    loc_a = Variable("loc_a", "location", attributes={"supply":0, "demand":0})
    person_a = Variable("person_a", "person", attributes={"trips-taken":0})
    
    args_assign = [person_a, car_a, loc_a, world]
    assign_precons = {"positive":[AtomicSentence("at", [car_a, loc_a]), AtomicSentence("at", [person_a, loc_a])], "negative":[AtomicSentence("is-assigned", [person_a])], "metrics":[]} 
    assign_effects = {"add":[AtomicSentence("assigned", [person_a, car_a]), AtomicSentence("is-assigned", [person_a])], "delete":[AtomicSentence("at", [person_a, loc_a])], "metrics":[]}
    
    assign_action = Action("Assign", args_assign, assign_precons, assign_effects)
    
    #bound_assign = get_bound_actions(assign_action, world_objects)
    #----------------------------------------
    
    #------------------
    
    #Initial state
    #------------------

    #Initialize objects
    #The World, Persons, locations, cars
    the_world = Variable("world", "domain", "The World", attributes={"number-trips":0})
    

    source_loc_1 = "1919 22nd Street, San Francisco, CA 94107"
    source_loc_2 = "mission st and cesar chavez st., San Francisco, CA 94110"

    dest_loc_1 = "65 9th Street, San Francisco, CA"
    dest_loc_2 = "668 Clay St, San Francisco, CA"

    person_1_home = "289 Hamilton Street, San Francisco, CA 94134"
    person_2_home = "289 Hamilton Street, San Francisco, CA 94134"
    person_3_home = "Palo Alto, CA"
    person_4_home = "Brisbane, CA"
    person_5_home = "Brisbane, CA"
    
    people = [Variable("person_a", "person", "Greg & David", attributes={"trips-taken":0, "home":person_1_home}),
             Variable("person_b", "person", "Kenny & Maria", attributes={"trips-taken":0, "home":person_2_home}), 
             Variable("person_c", "person", "Rona & David", attributes={"trips-taken":0, "home":person_3_home}),
             Variable("person_d", "person", "Leesa", attributes={"trips-taken":0, "home":person_4_home}),
             Variable("person_e", "person", "Cassandra", attributes={"trips-taken":0, "home":person_5_home})
             ]
    
    locations = [Variable("location_1", "location", source_loc_1, attributes={"supply":700, "demand":0}),
     Variable("location_2", "location", source_loc_2, attributes={"supply":1150, "demand":0}), 
     Variable("location_3", "location", dest_loc_1, attributes={"supply":0, "demand":800}),
     Variable("location_4", "location", dest_loc_2, attributes={"supply":0, "demand":1050}),
     Variable("location_5", "location", person_1_home, attributes={"supply":0, "demand":0}),
     Variable("location_6", "location", person_2_home, attributes={"supply":0, "demand":0}),
     Variable("location_7", "location", person_3_home, attributes={"supply":0, "demand":0}),
     Variable("location_8", "location", person_4_home, attributes={"supply":0, "demand":0}),
     Variable("location_9", "location", person_5_home, attributes={"supply":0, "demand":0})]
    
    cars = [Variable("car_1", "car", "Greg & David car'", attributes={"capacity":200}),
            Variable("car_2", "car", "Kenny & Maria car", attributes={"capacity":200}),
            Variable("car_3", "car", "Rona & David car", attributes={"capacity":350}),
            Variable("car_4", "car", "Leesa car", attributes={"capacity":200}),
            Variable("car_5", "car", "Cassandra car", attributes={"capacity":200})]

    people_locations = [AtomicSentence("at", [locations[4], people[0]]), 
                        AtomicSentence("at", [locations[5], people[1]]),
                        AtomicSentence("at", [locations[6], people[2]]),
                        AtomicSentence("at", [locations[7], people[3]]),
                        AtomicSentence("at", [locations[8], people[4]])]
    
    car_locations = [AtomicSentence("at", [locations[4], cars[0]]),
                    AtomicSentence("at", [locations[5], cars[1]]),
                    AtomicSentence("at", [locations[6], cars[2]]),
                    AtomicSentence("at", [locations[7], cars[3]]),
                    AtomicSentence("at", [locations[8], cars[4]])]

    #------------------

    #Goal
    #------------------

    #------------------

    objects = people
    objects.extend(locations)
    objects.extend(cars)
    objects.append(the_world)

    initial_state_val = people_locations
    initial_state_val.extend(car_locations)
    #initial_state_val.append(the_world)

    init_state = State(initial_state_val)
    
    init_state.metrics[the_world.bound_val] = {}
    init_state.metrics[the_world.bound_val]["number-trips"] = 0

    init_state.metrics[people[0].bound_val] = {}
    init_state.metrics[people[0].bound_val]["trips-taken"] = 0

    init_state.metrics[people[1].bound_val] = {}
    init_state.metrics[people[1].bound_val]["trips-taken"] = 0

    init_state.metrics[people[2].bound_val] = {}
    init_state.metrics[people[2].bound_val]["trips-taken"] = 0

    init_state.metrics[people[3].bound_val] = {}
    init_state.metrics[people[3].bound_val]["trips-taken"] = 0

    init_state.metrics[people[4].bound_val] = {}
    init_state.metrics[people[4].bound_val]["trips-taken"] = 0

    init_state.metrics[locations[0].bound_val] = {}
    init_state.metrics[locations[0].bound_val]["supply"] = 1000
    init_state.metrics[locations[0].bound_val]["demand"] = 0

    init_state.metrics[locations[1].bound_val] = {}
    init_state.metrics[locations[1].bound_val]["supply"] = 600
    init_state.metrics[locations[1].bound_val]["demand"] = 0

    init_state.metrics[locations[2].bound_val] = {}
    init_state.metrics[locations[2].bound_val]["supply"] = 0
    init_state.metrics[locations[2].bound_val]["demand"] = 800

    init_state.metrics[locations[3].bound_val] = {}
    init_state.metrics[locations[3].bound_val]["supply"] = 0
    init_state.metrics[locations[3].bound_val]["demand"] = 800

    init_state.metrics[locations[4].bound_val] = {}
    init_state.metrics[locations[4].bound_val]["supply"] = 0
    init_state.metrics[locations[4].bound_val]["demand"] = 0
    
    init_state.metrics[locations[5].bound_val] = {}
    init_state.metrics[locations[5].bound_val]["supply"] = 0
    init_state.metrics[locations[5].bound_val]["demand"] = 0

    init_state.metrics[locations[6].bound_val] = {}
    init_state.metrics[locations[6].bound_val]["supply"] = 0
    init_state.metrics[locations[6].bound_val]["demand"] = 0

    init_state.metrics[locations[7].bound_val] = {}
    init_state.metrics[locations[7].bound_val]["supply"] = 0
    init_state.metrics[locations[7].bound_val]["demand"] = 0

    init_state.metrics[locations[8].bound_val] = {}
    init_state.metrics[locations[8].bound_val]["supply"] = 0
    init_state.metrics[locations[8].bound_val]["demand"] = 0

    init_state.metrics[cars[0].bound_val] = {}
    init_state.metrics[cars[0].bound_val]["capacity"] = 150

    actions = [drive_action, load_action, unload_action, assign_action]    
    
    goal = None

    return actions,objects,init_state,goal

def main():
    (actions, objects, init_state, goal) = get_test_domain()

    aPlanner = Planner(actions, objects, init_state, goal)

if __name__ == "__main__":
    main()