'''
    PlannerManager - usage from client code:
    aPlanner = PlannerManager(data_dict)

    #This will block until complete.
    aPlanner.execute()

    return aPlanner.get_planner.output()
'''


import runtime
import logging
import subprocess
import re

from optparse import OptionParser

options_parser = OptionParser()
options_parser.add_option("-d", "--domain", action="store", type="string", dest="domain_file_path")

PLANNER_EXEC_COMMAND = runtime.get_planner_exec_path()

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)

class PlannerManager():

    def __init__(self, problem_data):
        """
        problem_data is a dict:

        problem_data:
            "persons"
            "locations"
            "cars"
            "at_persons": [(person, location), ...]
            "at_cars": [(car, location), ...]
            "car_capaities": [(car, capacity), ...]
            "supply_init": [(location, amount), ...]
            "demand_init": [(location, amount), ...]
        """

        logging.info("Initializing PlanningManager.")
        self.last_response = None
        self.problem_initial_data = problem_data
        self.problem_file_path = self.generate_problem_file()

    def get_strings_dictionary(self):
        """
            Examine self.problem_initial_data, and produce dictionary
            to be used by pddl generator
        """

        init_dict = {}

        #Objects
        #------------------
        init_dict["persons"] = " ".join(self.problem_initial_data["persons"])
        init_dict["locations"] = " ".join(self.problem_initial_data["locations"])
        init_dict["cars"] = " ".join(self.problem_initial_data["cars"])
        #------------------

        #Person init string
        #------------------
        init_dict["person_init_string"] = ""
        for p in self.problem_initial_data["persons"]:
            init_dict["person_init_string"]+=("(person %s)" % p)
            init_dict["person_init_string"]+="\n"
        #------------------

        #Location init string
        #--------------------
        init_dict["location_init_string"] = ""
        for l in self.problem_initial_data["locations"]:
            init_dict["location_init_string"]+=("(location %s)" % l)
            init_dict["location_init_string"]+="\n"
        #--------------------

        #Car init string
        #--------------------
        init_dict["car_init_string"] = ""
        for c in self.problem_initial_data["cars"]:
            init_dict["car_init_string"]+=("(car %s)" % c)
            init_dict["car_init_string"]+="\n"
        #--------------------

        #At person string
        #--------------------
        init_dict["at_person_strings"] = ""
        for entry in self.problem_initial_data["at_persons"]:
            init_dict["at_person_strings"]+="(at %s %s)" % (entry[0], entry[1])
            init_dict["at_person_strings"]+="\n"
        #--------------------

        #At car string
        #--------------------
        init_dict["at_car_strings"] = ""
        for entry in self.problem_initial_data["at_cars"]:
            init_dict["at_car_strings"]+="(at %s %s)" % (entry[0], entry[1])
            init_dict["at_car_strings"]+="\n"
        #--------------------

        #Supply init string
        #--------------------
        init_dict["supply_init_string"] = ""
        for entry in self.problem_initial_data["supply_init"]:
            init_dict["supply_init_string"]+="(= (supply %s) %s)" % (entry[0], entry[1])
            init_dict["supply_init_string"]+="\n"
        #--------------------

        #Demand init string
        #--------------------
        init_dict["demand_init_string"] = ""
        for entry in self.problem_initial_data["demand_init"]:
            init_dict["demand_init_string"]+="(= (demand %s) %s)" % (entry[0], entry[1])
            init_dict["demand_init_string"]+="\n"
        #--------------------

        #Car capacity init strings
        #--------------------
        init_dict["car_capacity_init_strings"] = ""
        for entry in self.problem_initial_data["car_capacities"]:
            init_dict["car_capacity_init_strings"]+="(= (car-capacity %s) %s)" % (entry[0], entry[1])
            init_dict["car_capacity_init_strings"]+="\n"
        #--------------------

        #Trips taken init strings
        #--------------------
        init_dict["trips_taken_init_strings"] = ""
        for p in self.problem_initial_data["persons"]:
            init_dict["trips_taken_init_strings"]+="(= (trips-taken %s) 0)" % p
            init_dict["trips_taken_init_strings"]+="\n"
        #--------------------

        #Goal statement string
        #---------------------
        #(<= (demand loc3) 0)
        init_dict["goal_statement"] = ""
        goal_statement_string = ""
        demand_locations = [pairs[0] for pairs in self.problem_initial_data["demand_init"]]

        if len(demand_locations)>1:
            goal_statement_string+="(and "
        
        for loc_name in demand_locations:
            string_for_subgoal = "(<= (demand %s) 0) " % loc_name
            goal_statement_string+=string_for_subgoal
        
        if len(demand_locations)>1:
            goal_statement_string+=")"
        
        init_dict["goal_statement"] = goal_statement_string
        #---------------------

        return init_dict

    def get_file_path(self):
        return "fr_problem_out.pddl"

    def generate_problem_file(self):
        logging.info("Creating problem file.")

        init_strings_dictionary = self.get_strings_dictionary()

        #Generate output string
        output_template = '''

        (define (problem foodrev-1)
            (:domain
                foodrev-domain
            )

            (:objects
                %(locations)s
                %(persons)s
                %(cars)s
            )

            (:init
                %(person_init_string)s
                %(location_init_string)s
                %(car_init_string)s

                %(at_person_strings)s
                %(at_car_strings)s

                %(supply_init_string)s
                %(demand_init_string)s

                %(car_capacity_init_strings)s

                %(trips_taken_init_strings)s

                (= (number-trips) 0)
            )

            (:goal
                %(goal_statement)s
            )

            (:metric minimize (number-trips))
        )
''' % init_strings_dictionary

        logging.info("Created problem file string: ")
        logging.info(output_template)

        file_path_name = self.get_file_path()

        #Write string to file
        #--------------------
        logging.info("Writing problem file to disk.")
        with open(file_path_name, "w") as out_f:
            out_f.write(output_template)
        logging.info("Completed writing problem file.")
        #--------------------

        #Return file path
        return file_path_name


    def execute(self):
        logging.info("Executing planner.")
        #Set temporary file

        #Execute planner
        args_dict = {"domain_file_path":runtime.get_domain_file_path(), "problem_file_path":self.problem_file_path}
        complete_command_string = PLANNER_EXEC_COMMAND+" -o %(domain_file_path)s -f %(problem_file_path)s" % args_dict

        logging.info("Executing %s " % complete_command_string)

        proc = subprocess.Popen(complete_command_string.split(), stdout=subprocess.PIPE)
        proc_vals = proc.communicate()

        output = proc_vals[0]
        
        output_json = self.process_planner_output(output)

        return output_json
    
    def process_planner_output(self, output_str):
        return_dict = {}

        status = None
        if output_str.find("found legal plan")!=-1:
            status = "success"
        else:
            status = "fail"

        return_dict["plan_status"] = status
        return_dict["plan_steps"] = []

        output_lines = output_str.split("\n")
        for line in output_lines:
            stripped_line = line.strip()

            line_parts = stripped_line.split()
            
            if len(line_parts)>0:
                first_part = line_parts[0]
                first_part = first_part.lstrip("step")
                first_part = first_part.strip()
                if re.search('(\d)+:', first_part) is not None:
                    return_dict["plan_steps"].append(stripped_line)

        return return_dict

def run_test():
    import json

    print "Executing test."
    (options, args) = options_parser.parse_args()
    domain_file_path = options.domain_file_path

    problem_dict = {}
    with open(domain_file_path) as input_file:
        problem_dict = json.load(input_file)

    pm = PlannerManager(problem_dict)

    pm.execute()
    
    print "Test complete."

def main():
    run_test()

if __name__=="__main__":
    main()
