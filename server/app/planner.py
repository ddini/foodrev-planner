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
        self.num_array = value
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

        num_violations = 0

        min_val = min(self.num_array)
        max_val = max(self.num_array)

        mod1 = math.fabs(self.num_array[0] - min_val)
        mod2 = math.fabs(self.num_array[-1] - max_val)

        for i in range(len(self.num_array)):
            if i<len(self.num_array)-1:
                if self.num_array[i]>self.num_array[i+1]:
                    num_violations+=1
        
        return num_violations + mod1 + mod2
    
    def __str__(self):
        return "state: %s h:%s" % (str(self.num_array), str(self.h()))

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

    def __init__(self, actions, init_state):
        self.state_pq = PriorityQueue()
        self.state_pq.put( (init_state.h(), init_state) )
        self.actions = actions
    
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

def get_bound_actions(action, world_objects):
    pass

def main():
    
    #Initialize objects
    #------------------
    objects = []

    #------------------

    #Create every bound version of action
    #------------------
    # (:action load
	# 	:parameters (?car ?location)
	# 	:precondition (and
	# 				(> (supply ?location) 0)
	# 				(at ?car ?location)
	# 				(location ?location)
	# 				(car ?car)
	# 				(not (carrying-load ?car))
	# 			)

	# 	:effect (and
	# 			(decrease (supply ?location) (car-capacity ?car))
	# 			(carrying-load ?car)
	# 		)
	# )

    #Drive
    #----------------------------------------
    person_a = Variable("person_a", "person")
    loc_from = Variable("from_loc", "location")
    loc_to = Variable("to_loc", "location")
    car_a = Variable("car_a", "car")

    args_drive = [person_a, car_a, loc_from, loc_to]
    drive_precons = [AtomicSentence("at", [car_a, loc_from] ), AtomicSentence("assigned", [person_a, car_a])]
    drive_effects = {"add":[AtomicSentence("at", [car_a, loc_to])], "delete":[AtomicSentence("at", [car_a, loc_from])]}

    drive_action = Action("Drive", args_drive, drive_precons, drive_effects)
    #bound_drive = get_bound_actions(drive_action, world_objects)
    #----------------------------------------
    
    #Load
    #---------------------------------------- 
    car_a = Variable("car-a", "car")
    loc_a = Variable("loc-a", "location")
    args_load = [car_a, loc_a]
    load_precons = [AtomicSentence("at", [car_a, loc_a]), AtomicSentence("carrying-load", [car_a], negation=True)]
    load_effects = {"add":AtomicSentence("carrying-load", [car_a]), "delete":[]}
    load_action = Action("Load", args_load, load_precons, load_effects)
    #bound_load = get_bound_actions(load_action, world_objects)
    #----------------------------------------

    #Unload
    #----------------------------------------
    args_unload = []
    unload_action = Action("Unload", args_unload, unload_precons, unload_effects)
    #bound_unload = get_bound_actions(unload_action, world_objects)
    #----------------------------------------

    #Assign
    #----------------------------------------
    args_assign = []
    assign_action = Action("Assign", args_assign, assign_precons, assign_effects)
    #bound_assign = get_bound_actions(assign_action, world_objects)
    #----------------------------------------
    
    #------------------
    
    #Initial state
    #------------------

    #------------------

    #Goal
    #------------------

    #------------------

    aPlanner = Planner(actions, objects, initial_state, goal)

if __name__ == "__main__":
    main()