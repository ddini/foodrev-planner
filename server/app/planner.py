import itertools

from copy import deepcopy
from Queue import PriorityQueue
import math

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
    
    def enumerate_plan(self):

        acc_list = []

        curr_node = self
        while curr_node.prev_state is not None:
            acc_list.append(curr_node.prev_action)
            curr_node = curr_node.prev_state

        return acc_list
    
    def h(self):
        return 0
    
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
        if self.attributes is not None:
            return_str+="\n"
            return_str+=(",".join([ str(k)+":"+str(self.attributes[k]) for k in self.attributes ]))
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
        
        #Dictionary of two lists, keyed as "add" and "delete", each of AtomicSentence instances
        self.effects = effects
    
    def bind(self, **term_bindings):

        #Bind terms in term list
        for t in self.terms:
            term_name = t.name
            if term_name in term_bindings:
                bound_term = term_bindings[term_name]
                t.bound_val = bound_term.bound_val
                t.attributes = bound_term.attributes
    
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
        print "Call to get_bound_actions_for_unbound: %s" % str(unbound_act)

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
        print "Call to get_bound_actions"

        for a in self.actions:
            bound_actions = self.get_bound_actions_for_unbound(a)
            self.bound_acts_dict[a] = bound_actions
        
        for k in self.bound_acts_dict:
            self.all_bound_actions.extend(self.bound_acts_dict[k])
    
    def goal_is_met(self, aState):
        return_val = False

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
                break
        #----------------------
        
        #negative preconditions
        #----------------------
        negative_precons = bound_action.preconditions["negative"]

        for n in negative_precons:
            if n in state_AS_list:
                conditions_are_met = False
                break
        #----------------------

        metric_precons = bound_action.preconditions["metrics"]

        return conditions_are_met

    
    def act_on(self, bound_action, state_node):
        new_state_node = None

        new_state_node = deepcopy(state_node)

        add_effects = bound_action.effects["add"]
        new_state_node.value.extend(add_effects)

        delete_effects = bound_action.effects["delete"]

        items_to_remove = []
        for element in new_state_node.value:
            if element in delete_effects:
                items_to_remove.append(element)

        for i in items_to_remove:
            new_state_node.value.remove(i)
        
        return new_state_node
    
    def execute(self):
        
        current_node = self.state_pq.get()
        current_node = current_node[1]

        while (current_node is not None) and (not self.goal_is_met(current_node)):
            print "current node: %s" % current_node
            for a in self.all_bound_actions:
                if self.preconditions_are_met(a, current_node):
                    
                    new_state = self.act_on(a, current_node)

                    new_state.prev_state = current_node
                    new_state.prev_action = a

                    self.state_pq.put((new_state.h(), new_state))
            
            if not self.state_pq.empty(): 
                current_node = self.state_pq.get()
                current_node = current_node[1]
            else:
                current_node = None

        return current_node

def effect_function(**args):
    """ Specified on a per domain basis """
    pass

def get_test_domain():
    #Drive
    #----------------------------------------
    world = Variable("world", "domain", attributes={"number-trips":0})

    person_a = Variable("person_a", "person", attributes={"trips-taken":0})
    loc_from = Variable("from_loc", "location", attributes={"supply":0, "demand":0})
    loc_to = Variable("to_loc", "location", attributes={"supply":0, "demand":0})
    car_a = Variable("car_a", "car")

    args_drive = [person_a, car_a, loc_from, loc_to]
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
    
    car_a = Variable("car_a", "car", attributes={"capacity":0})
    loc_a = Variable("loc_a", "location", attributes={"supply":0, "demand":0})
    args_load = [car_a, loc_a]
    load_precons = {"positive":[AtomicSentence("at", [car_a, loc_a]), AtomicSentence("carrying-load", [car_a])], "negative":[],
                        "metrics":[
                                {"object":loc_a, "attribute":"supply", "operation":"gt", "value":0}
                            ] 
                    }
    load_effects = {"add":[AtomicSentence("carrying-load", [car_a])], "delete":[], 
                        "metrics":[
                            {"object":loc_a, "attribute":"supply", "impact":-1*car_a.attributes["capacity"]}
                            ] 
                    }
    load_action = Action("Load", args_load, load_precons, load_effects)
    #bound_load = get_bound_actions(load_action, world_objects)
    #----------------------------------------

    #Unload
    #----------------------------------------
    # (:action unload
    # :parameters (?car ?location)
    # :precondition (and
    #             (> (demand ?location) 0)
    #             (carrying-load ?car)
    #             (location ?location)
    #             (car ?car)
    #             (at ?car ?location)
    #         )
    # :effect (and
    #         (decrease (demand ?location) (car-capacity ?car))		
    #         (not (carrying-load ?car))
    #     )
	# )
    
    world = Variable("world", "domain", attributes={"number-trips":0})
    
    car_a = Variable("car_a", "car", attributes={"capacity":0})
    loc_a = Variable("loc_a", "location", attributes={"supply":0, "demand":0})
    args_unload = [car_a, loc_a]
    
    unload_precons = {"positive":[AtomicSentence("carrying-load", [car_a]), AtomicSentence("at", [car_a, loc_a])], "negative":[], 
                "metrics":[ {"object":loc_a, "attribute":"demand", "operation":"gt", "value":0} ]
                }
    unload_effects = {"add":[], "delete":[AtomicSentence("carrying-load", [car_a])], 
                "metrics":[{"object":loc_a, "attribute":"demand", "impact":-1*car_a.attributes["capacity"]}
    ]}

    unload_action = Action("Unload", args_unload, unload_precons, unload_effects)
    #bound_unload = get_bound_actions(unload_action, world_objects)
    #----------------------------------------

    #Assign
    #----------------------------------------
    world = Variable("world", "domain", attributes={"number-trips":0})
    
    car_a = Variable("car_a", "car", attributes={"capacity":0})
    loc_a = Variable("loc_a", "location", attributes={"supply":0, "demand":0})
    person_a = Variable("person_a", "person", attributes={"trips-taken":0})
    
    args_assign = [person_a, car_a, loc_a]
    assign_precons = {"positive":[AtomicSentence("at", [car_a, loc_a]), AtomicSentence("at", [person_a, loc_a])], "negative":[AtomicSentence("is-assigned", [person_a])]} 
    assign_effects = {"add":[AtomicSentence("assigned", [person_a, car_a]), AtomicSentence("is-assigned", [person_a])], "delete":[AtomicSentence("at", [person_a, loc_a])]}
    
    assign_action = Action("Assign", args_assign, assign_precons, assign_effects)
    
    #bound_assign = get_bound_actions(assign_action, world_objects)
    #----------------------------------------
    
    #------------------
    
    #Initial state
    #------------------
    
    #List of AtomicSentence instances
    # {
    # "persons":["Alice", "Bob", "Charlie"],
    # "locations":["loc1", "loc2", "loc3"],
    # "cars":["car1", "car2"],
    # "at_persons":[["Alice","loc1"], ["Bob", "loc1"], ["Charlie", "loc1"]],
    # "at_cars":[["car1", "loc1"], ["car2", "loc2"]],
    # "car_capacities":[["car1", 100], ["car2", 100]],
    # "supply_init":[["loc2", 200]],
    # "demand_init":[["loc3", 200]]
    # }

    #Initialize objects
    #The World, Persons, locations, cars
    the_world = Variable("world", "Domain", "The World", attributes={"number-trips":0})
    
    people = [Variable("person_a", "person", "Alice", attributes={"trips-taken":0}), Variable("person_b", "person", "Bob", attributes={"trips-taken":0}), Variable("person_c", "person", "Charlie", attributes={"trips-taken":0})]
    locations = [Variable("location_1", "location", "Location 1", attributes={"supply":200, "demand":0}), Variable("location_2", "location", "Location 2", attributes={"supply":0, "demand":200})]
    cars = [Variable("car_1", "car", "Alices car", attributes={"capacity":50})]

    people_locations = [AtomicSentence("at", [locations[0], people[0]]), AtomicSentence("at", [locations[1], people[1]])]
    car_locations = [AtomicSentence("at", [locations[0], cars[0]])]

    #------------------

    #Goal
    #------------------

    #------------------

    objects = people
    objects.extend(locations)
    objects.extend(cars)

    initial_state_val = people_locations
    initial_state_val.extend(car_locations)
    initial_state_val.append(the_world)

    init_state = State(initial_state_val)
    
    actions = [drive_action, load_action, unload_action, assign_action]    
    
    goal = None

    return actions,objects,init_state,goal

def main():
    (actions, objects, init_state, goal) = get_test_domain()

    aPlanner = Planner(actions, objects, init_state, goal)

if __name__ == "__main__":
    main()