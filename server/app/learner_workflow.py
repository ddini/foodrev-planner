
import math

import planner
import problem_parser

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


def extract_features_from_plan(aPlan):

    feature_vector = []

    #Total number trips
    f1 = aPlan.metrics["The World"]["number-trips"]

    #Trip entropy measure
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

    #Sum of distances between final location and home location
    #---------------------------------------------------------
    #final location of each car

    #Who is in each car
    
    #final location of each person

    #home location of each person

    #Find difference in locations

    f3 = None
    #---------------------------------------------------------

    #(Final loc - Home loc) distance entropy measure
    #-----------------------------------------------
    
    
    f4 = None 
    #-----------------------------------------------

    feature_vector = (f1, f2, f3, f4)

    return feature_vector

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