
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
    
    frPlanner.find_plans(q_hat)

    #From above plans, select k, sampling from space determined
    #by features, f1, f2, f3, f4.
    sampled_plans = frPlanner.sample_plans(num_plans=4)

    #Present k plans to human operator for scoring.
    return sampled_plans


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