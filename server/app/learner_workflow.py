
import math
import logging

import planner
import problem_parser

import googlemapsAtoB

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)


#Workflow
def workflow():
    #Receive partially specified problem
    initial_problem_dict = {}

    #Action 1 - select problem completion
    complete_problem_dict = select_problem_completion(initial_problem_dict)

    #Generate some number of plans meeting outstanding demand
    (actions, objects, init_state, goal) = problem_parser.parse_dict(complete_problem_dict)
    frPlanner = Planner(actions, objects, init_state, goal)
    
    plans = frPlanner.execute(plans_to_find=100)

    #Resolve plans into features
    plans_by_feature = [(features,plan_id) for p in plans]

    #Choose k-plans by epsilon-greedy policy
    #---------------------------------------
    scored_plans = [(q_hat(p), p) for p in plans_by_feature]

    #Sort plans_by_feature by q_hat
    scored_plans.sort(reverse=True)

    #Take top k-1 and one random one
    sampled_plans = []
    #---------------------------------------

    #Present k plans to human operator for scoring.
    return sampled_plans


def extract_features_from_plan(aPlan, world_objects):

    feature_vector = []

    #Feature 1: Total number trips
    f1 = aPlan.metrics["The World"]["number-trips"]

    #Feature 2: Trip entropy measure
    #--------------------
    person_trips = []

    #Collect number of trips per person
    for k in aPlan.metrics:
        if "trips-taken" in aPlan.metrics[k]:
            trips_for_person = aPlan.metrics[k]["trips-taken"]
            person_trips.append(trips_for_person)
    
    #Nomralize values as if probability distribution
    total_trips = float(f1)
    noralized_per_person_trips = [float(v)/total_trips for v in person_trips]

    #Evaluate entropy
    entropy_acc = 0
    for v in noralized_per_person_trips:
        if v!=0:
            entropy_acc+=-1*v*math.log(v,2)
        else:
            entropy_acc+=0

    f2 = entropy_acc
    #--------------------

    #Feature 3: Sum of distances between final location and home location
    #---------------------------------------------------------
    
    #final location of each car
    car_to_loc = {}
    for atom_sent in aPlan.value:
        if atom_sent.name=="at":
            car_terms = [t for t in atom_sent.terms if t.type=="CAR"]
            loc_terms = [t for t in atom_sent.terms if t.type=="LOCATION"]
            
            if len(car_terms)>0:
                car_term = car_terms[0]
                loc_term = loc_terms[0]
                car_to_loc[car_term.bound_val] = loc_term.bound_val

    #Who is in each car
    person_to_car = {}
    for atom_sent in aPlan.value:
        if atom_sent.name=="assigned":
            person_terms = [t for t in atom_sent.terms if t.type=="PERSON"]
            car_terms = [t for t in atom_sent.terms if t.type=="CAR"]

            if len(person_terms)>0:
                person_term = person_terms[0]
                car_term = car_terms[0]
                person_to_car[person_term.bound_val] = car_term.bound_val

    #final location of each person
    person_to_loc = {}
    for p in person_to_car:
        person_to_loc[p] = car_to_loc[person_to_car[p]]

    person_to_home_loc = {}
    #home location of each person
    for obj in world_objects:
        if obj.type=="PERSON":
            home_location = obj.attributes["home"]
            person_to_home_loc[obj.bound_val] = home_location

    #Find difference in locations
    terminus_home_diffs = []
    
    for p in person_to_loc:
        dist_diff = get_distance(person_to_loc[p], person_to_home_loc[p])
        terminus_home_diffs.append(dist_diff)

    f3 = reduce(lambda x,y:x+y, terminus_home_diffs)
    #---------------------------------------------------------

    #Feature 4: (Final loc - Home loc) distance entropy measure
    #-----------------------------------------------
    #Nomralize values as if probability distribution
    total_diffs = float(f3)
    if total_diffs == 0:
        f4 =  0
    else:
        noralized_per_person_diffs = [float(v)/total_diffs for v in terminus_home_diffs]

        #Evaluate entropy
        entropy_acc = 0
        for v in noralized_per_person_diffs:
            if v!=0:
                entropy_acc+=-1*v*math.log(v,2)
            else:
                entropy_acc+=0

        f4 = entropy_acc
    #-----------------------------------------------

    feature_vector = (f1, f2, f3, f4)

    return feature_vector

def get_distance(loc_a_str, loc_b_str):
    logging.info("get_distance: %s, %s" % (loc_a_str, loc_b_str))

    dist_api = googlemapsAtoB.GoogleMapsAtoB(loc_a_str, loc_b_str, "AIzaSyANdUjfLpgjP5tkDXR2TLSiD3NHNjuBRPU")

    time_to_travel = dist_api.get_time()

    return time_to_travel

def select_problem_completion(problem_dict):
    pass

    #Find locations for which demand is not specified.

    #Select some way to distribute supply among locations.

    #Return completed dictionary.

def apply_score(plan_id, score):
    #Update q_hat(act1, f1, f2, f3, f4)
    pass

def q_hat(feature_vector):
    pass

if __name__ == "__main__":
    workflow()