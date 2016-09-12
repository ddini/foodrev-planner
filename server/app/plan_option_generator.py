
class PlanOptionGenerator():

    def __init__(self, problem_data):
        """ 
            'problem_data' is a dictionary containing an underspecified problem.
        """
        self.problem_data = problem_data
    
    def execute(self):
        response_dict = {}

        response_dict["options"] = []

        for plan in plan_options:
            plan_dict = {}
            plan_dict["plan_id"] = self.get_plan_id()
            plan_dict["plans"] = []
            plan_dict["ending_locations"] = {}
            plan_dict["num_trips"] = {}

            response_dict["options"].append(plan_dict)
        
        return response_dict
