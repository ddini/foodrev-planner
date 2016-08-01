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
