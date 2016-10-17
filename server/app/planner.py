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
    def __init__(self, name, var_type=None, value=None):
        self.name = name
        self.type = var_type
        self.bound_val = value
    
    def __str__(self):
        return_str = "%(name)s : %(var_type)s - %(b_val)s" % {"name":self.name, "var_type":self.type.upper(), "b_val":self.bound_val}
        return return_str

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
        print "Bind: "
        for k in term_bindings:
            print "%s --> %s" % (k, str(term_bindings[k]))

        #Bind terms in term list
        for t in self.terms:
            term_name = t.name
            if term_name in term_bindings:
                term_val = term_bindings[term_name]
                t.bound_val = term_val
    
    def __str__(self):
        return_str = "Action: %(name)s (" % {"name":self.name}
        # for t in self.terms:
        #     return_str+="%(term_name)s:%(term_type)s:%(term_val)s " % {"term_name":t.name, "term_type":t.type.upper(), "term_val":t.bound_val}
        
        return_str+=", ".join([str(t) for t in self.terms])
        return_str+=")"
    
        
        return return_str

class Planner():

    def __init__(self, actions, world_objects, init_state, goal):
        self.state_pq = PriorityQueue()
        self.state_pq.put( (init_state.h(), init_state) )
        
        self.actions = actions
        self.goal = goal
        self.w_objects = world_objects

        #Action --> [bound_action, bound_action, ...]
        self.bound_acts_dict = {}
    
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
                bindings_dict[term_param.name] = bound_parameter.bound_val

            act_copy.bind(**bindings_dict)
            
            bound_actions.append(act_copy)

        return bound_actions

    
    def set_bound_actions(self):
        print "Call to get_bound_actions"

        for a in actions:
            bound_actions = self.get_bound_actions_for_unbound(a)
            self.bound_acts_dict[a] = bound_actions
    
    def goal_is_met(self, aState):
        
        num_array = aState.num_array

        return_val = True

        for i in range(len(num_array)):
            if i<len(num_array)-1:
                if num_array[i]>num_array[i+1]:
                    return_val = False
                    break

        return return_val
    
    def execute(self):
        
        current_node = self.state_pq.get()
        current_node = current_node[1]

        while (current_node is not None) and (not self.goal_is_met(current_node)):
            print "current node: %s" % current_node
            for a in self.actions:
                new_state = a.act_on(current_node)

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
    person_a = Variable("person_a", "person")
    loc_from = Variable("from_loc", "location")
    loc_to = Variable("to_loc", "location")
    car_a = Variable("car_a", "car")

    args_drive = [person_a, car_a, loc_from, loc_to]
    drive_precons = {"positive":[AtomicSentence("at", [car_a, loc_from] ), AtomicSentence("assigned", [person_a, car_a])], "negative":[] }
    drive_effects = {"add":[AtomicSentence("at", [car_a, loc_to])], "delete":[AtomicSentence("at", [car_a, loc_from])]}

    drive_action = Action("Drive", args_drive, drive_precons, drive_effects)
    #bound_drive = get_bound_actions(drive_action, world_objects)
    #----------------------------------------
    
    #Load
    #---------------------------------------- 
    car_a = Variable("car_a", "car")
    loc_a = Variable("loc_a", "location")
    args_load = [car_a, loc_a]
    load_precons = {"positive":[AtomicSentence("at", [car_a, loc_a]), AtomicSentence("carrying-load", [car_a])], "negative":[]}
    load_effects = {"add":[AtomicSentence("carrying-load", [car_a])], "delete":[]}
    load_action = Action("Load", args_load, load_precons, load_effects)
    #bound_load = get_bound_actions(load_action, world_objects)
    #----------------------------------------

    # (:action unload
	# 	:parameters (?car ?location)
	# 	:precondition (and
	# 				(> (demand ?location) 0)
	# 				(carrying-load ?car)
	# 				(location ?location)
	# 				(car ?car)
	# 				(at ?car ?location)
	# 			)
	# 	:effect (and
	# 			(decrease (demand ?location) (car-capacity ?car))		
	# 			(not (carrying-load ?car))
	# 		)
	# )

    #Unload
    #----------------------------------------
    car_a = Variable("car_a", "car")
    loc_a = Variable("loc_a", "location")
    args_unload = [car_a, loc_a]
    
    unload_precons = {"positive":[AtomicSentence("carrying-load", [car_a]), AtomicSentence("at", [car_a, loc_a])], "negative":[]}
    unload_effects = {"add":[], "delete":[AtomicSentence("carrying-load", [car_a])]}

    unload_action = Action("Unload", args_unload, unload_precons, unload_effects)
    #bound_unload = get_bound_actions(unload_action, world_objects)
    #----------------------------------------


    # (:action assign-car
	# 	:parameters (?person ?car ?location)
	# 	:precondition (and
	# 				(person ?person)
	# 				(car ?car)
	# 				(not (is-assigned ?person))
	# 				(at ?car ?location)
	# 				(at ?person ?location)
	# 			)
	# 	:effect (and
	# 			(assigned ?person ?car)
	# 			(is-assigned ?person)
	# 			(not (at ?person ?location))
	# 		)
	# )

    #Assign
    #----------------------------------------
    car_a = Variable("car_a", "car")
    loc_a = Variable("loc_a", "location")
    person_a = Variable("person_a", "person")
    
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
    #Persons, locations, cars
    people = [Variable("person_a", "person", "Alice"), Variable("person_b", "person", "Bob"), Variable("person_c", "person", "Charlie")]
    locations = [Variable("location_1", "location", "Location 1"), Variable("location_2", "location", "Location 2")]
    cars = [Variable("car_1", "car", "Alices car")]

    people_locations = [AtomicSentence("at", [locations[0], people[0]]), AtomicSentence("at", [locations[1], people[1]])]
    car_locations = [AtomicSentence("at", [locations[0], cars[0]])]

    #------------------

    #Goal
    #------------------

    #Collection of AtomicSentence instances, possibly including metric statements.

    #------------------

    objects = people
    objects.extend(locations)
    objects.extend(cars)

    initial_state_val = people_locations
    initial_state_val.extend(car_locations)

    init_state = State(initial_state_val)
    
    actions = [drive_action, load_action, unload_action, assign_action]    
    
    goal = None

    return actions,objects,init_state,goal

def main():
    (actions, objects, init_state, goal) = get_test_domain()

    aPlanner = Planner(actions, objects, init_state, goal)

if __name__ == "__main__":
    main()