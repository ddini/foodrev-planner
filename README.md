# foodrev-planner

###     1       Launching the server

#### Environment variables
* 'PLANNER_EXEC_PATH': This is the (absolute) path to the FF metric planner executable.
* 'DOMAIN_FILE_PATH': This is the (absolute) path to the domain PDDL file.

An example of a complete invocation from the command line:

    PLANNER_EXEC_PATH=<path to FF executable> DOMAIN_FILE_PATH=<path to domain PDDL file> python run.py

This will listen by default on the port 5000 for requests.

###     2       Issuing requests and receving responses

A request to the planning server is issued in the form of a JSON document, as the payload in a PUT request to the /plan URL.

e.g.

        curl -X PUT -H "Content-Type: application/json" -d <quoted json document string> http://<server address>:<port number>/plan

An example JSON document describing a coordination task:

        {
          "persons":["Alice", "Bob", "Charlie"],
          "locations":["loc1", "loc2", "loc3"],
          "cars":["car1", "car2"],
          "at_persons":[["Alice","loc1"], ["Bob", "loc1"], ["Charlie", "loc1"]],
          "at_cars":[["car1", "loc1"], ["car2", "loc2"]],
          "car_capacities":[["car1", 100], ["car2", 100]],
          "supply_init":[["loc2", 200]],
          "demand_init":[["loc3", 200]]
        }

The response from the planning server for the above would is:

        {
            'plan_status': 'success', 
            'plan_steps': [
                    '1: DRIVE CHARLIE CAR1 LOC1 LOC2', 
                    '2: LOAD CAR1 LOC2', 
                    '3: DRIVE CHARLIE CAR1 LOC2 LOC3', 
                    '4: UNLOAD CAR1 LOC3', 
                    '5: DRIVE CHARLIE CAR1 LOC3 LOC2', 
                    '6: LOAD CAR1 LOC2', 
                    '7: DRIVE CHARLIE CAR1 LOC2 LOC3', 
                    '8: UNLOAD CAR1 LOC3']
        }
