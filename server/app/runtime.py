import os

def get_planner_exec_path():
    #If an environment variable is set,
    #then use that.
    command_path = os.environ.get("PLANNER_EXEC_PATH")

    if command_path is None:
        command_path = "./ff"

    return command_path

def get_domain_file_path():
    file_path = os.environ.get("DOMAIN_FILE_PATH")

    if file_path is None:
        file_path = "./foodrev_domain.pddl"
    
    return file_path
