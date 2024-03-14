""" state_machine.py
    The state_machine is the force behind creating and defining each state
    """

from .state import Predicate, State
from .visualization import run_visualization
import re
from prettytable import PrettyTable

INF = "inf"

class StateMachine:

    def __init__(self, max_t = 50):
        """
            scenario = the scenario defined by the user
            max_t = the maximum time step the StateMachine will run to
            states = pre-made list of empty states
        """
        self.max_t = max_t
        self.rules = []
        self._predicates = None
        self._sorts = None
        self._states = None

    @property
    def predicates(self):
        return self._predicates

    @predicates.setter
    def predicates(self, predicates):
        self._predicates = predicates
        self.show_debug_info_predicates()

    @property
    def sorts(self):
        return self._sorts
    
    @sorts.setter
    def sorts(self, sorts):
        self._sorts = sorts
        self.show_debug_info_sorts()

    @property
    def scenario(self):
        return self._scenario
    
    @scenario.setter
    def scenario(self, scenario):
        self.states = self.create_states()
        self.fill_states(scenario)
        self._scenario = scenario


    @staticmethod
    def filter_predicate_sorts(predicate):
        """
            retrieve the values the sort can have
        """
        predicate = re.search("{([^}]+)}", predicate)
        predicate_sorts = predicate.group(1).split(",")
        predicate_sorts = [value.strip() for value in predicate_sorts]
        return predicate_sorts

    def create_predicate_dict(self, predicates):
        """
            create a dictionary for the predicates from the predicates file
        """
        predicates = open(predicates, "r").read().splitlines()
        predicates = [line for line in predicates if line != ""]
        predicate_dic = {}
        for predicate in predicates:
            predicate = predicate.split(";")
            predicate_name = predicate[0]
            predicate_sorts = self.filter_predicate_sorts(predicate[1])
            predicate_dic[predicate_name] = predicate_sorts
        return predicate_dic

    @staticmethod
    def filter_sort_values(sort):
        """
            retrieve the values the sort can have
        """
        sort = re.search("{([^}]+)}", sort)
        sort_values = sort.group(1).split(",")
        sort_values = [value.strip() for value in sort_values]
        return sort_values

    def sort_sorts(self, sorts):
        """
            create a dictionary of sorts from the sorts file
        """
        sorts = open(sorts, "r").read().splitlines()
        sorts = [line for line in sorts if line != ""]
        sorts_dic = {}
        for sort in sorts:
            sort = sort.split(";")
            sort_name = sort[0]
            sort_values = self.filter_sort_values(sort[1])
            sorts_dic[sort_name] = sort_values
        return sorts_dic

    def create_states(self):
        """
            create "max_t" number of empty states
            State(i + 1), because it ranges from 0 - max_t, but states start from 1
        """
        states = []
        for i in range(self.max_t):
            states.append(State(i + 1, self.predicates, self.sorts))
        return states

    def check_validity_pred(self, predicate_name, agent, value):
        """
            check the validity of the predicate, based on the predicate name and the sorts
        """
        if predicate_name[0] not in self.predicates:
            print("The predicate \"%s\" is not a valid predicate (when loading the scenario file)." % predicate_name)
            print("The valid predicates are: ", end="")
            print(", ".join(self.predicates))
            return
        if len(predicate_name) > 1:
            # check which sorts should be in the nested predicate (to check for the agents)
            sorts_of_pred = self.predicates[predicate_name[-1]]
            if predicate_name[-1] not in self.predicates:
                print(
                    "The predicate \"%s\" is not a valid predicate within the predicate %s (when loading the scenario"
                    " file)." % (predicate_name[-1], predicate_name[0]))
                print("The valid predicates are: ", end="")
                print(", ".join(self.predicates))
                return
        else:
            sorts_of_pred = self.predicates[predicate_name[0]]
        # check validity agents
        for i in range(len(agent)):
            if sorts_of_pred[i] != "AGENT":
                print("Expected sort: AGENT, got sort: sort %s, for predicate %s on place %d, "
                      "when loading the scenario file" % (sorts_of_pred[i], predicate_name, i + 1))
            elif agent[i] not in self.sorts[sorts_of_pred[i]]:
                print("Agent %s does not seem to exist in the AGENT sorts, when loading the scenario file" % agent[i])
        if len(predicate_name) == 1:
            # check validity value of the sort (only if it is not nested)
            if sorts_of_pred[-1] == "BOOLEAN":
                if type(value) != bool:
                    print("Expected sort: BOOLEAN, got a different sort (with value %s), for predicate %s, "
                          "when loading the scenario file" % (value, predicate_name))
            elif sorts_of_pred[-1] == "REAL":
                if not ((type(value) == int) ^ (type(value) == float)):
                    print("Expected sort: REAL, got a different sort (with value %s), for predicate %s, "
                          "when loading the scenario file" % (value, predicate_name))
            elif value not in self.sorts[sorts_of_pred[-1]]:
                print("Expected sort: %s, got a different sort (with value %s), for predicate %s, "
                      "when loading the scenario file" % (sorts_of_pred[-1], value, predicate_name))


    def fill_states(self, scenario):
        """
            fill states based on solely the scenario file
        """
        
        for predicate in scenario:
            time_steps = predicate[-1]
            if type(predicate[1]) == tuple:
                predicates, agent, value = self.filter_nested_predicate_info(predicate)
            else:
                agent, value = self.filter_predicate_info(predicate[1])
                predicates = [predicate[0]]
            start_time, end_time = self.filter_predicate_time(time_steps)
            self.check_validity_pred(predicates, agent, value)
            self.insert_predicate(predicates, agent, value, start_time, end_time)

    def show_debug_info(self):
        """
            print debug information (defined sorts & defined predicates)
        """
        print("The StateMachine runs in Debug mode!\n")

        # create the pretty table of sorts and predicates
        sorts_table = PrettyTable()
        predicates_table = PrettyTable()

        # adding the field names of the table
        sorts_table.field_names = ["Sort name", "Sort values"]
        predicates_table.field_names = ["Predicate name", "Sorts"]

        # filling the sort table
        for sort in self.sorts:
            sorts_table.add_row([sort, ", ".join(self.sorts[sort].copy())])

        # filling the predicate table
        for predicate in self.predicates:
            predicates_table.add_row([predicate, str(self.predicates[predicate])])
        
        print("The StateMachine contains the following defined sorts, besides BOOLEAN and REAL: ")
        print(sorts_table)

        print("\nThe StateMachine contains the following predicates with their corresponding sorts: ")
        print(predicates_table)

    def show_debug_info_sorts(self):
        """
            print debug information (defined sorts & defined predicates)
        """
        

        # create the pretty table of sorts and predicates
        sorts_table = PrettyTable()
        

        # adding the field names of the table
        sorts_table.field_names = ["Sort name", "Sort values"]
        

        # filling the sort table
        for sort in self.sorts:
            sorts_table.add_row([sort, ", ".join(self.sorts[sort].copy())])
        
        print("The StateMachine contains the following defined sorts, besides BOOLEAN and REAL: ")
        print(sorts_table)

    def show_debug_info_predicates(self):
        """
            print debug information (defined sorts & defined predicates)
        """
        

        # create the pretty table of sorts and predicates
        predicates_table = PrettyTable()

        # adding the field names of the table
        predicates_table.field_names = ["Predicate name", "Sorts"]

        # filling the predicate table
        for predicate in self.predicates:
            predicates_table.add_row([predicate, str(self.predicates[predicate])])
        
        print("\nThe StateMachine contains the following predicates with their corresponding sorts: ")
        print(predicates_table)
        
        unique_sorts = set()

        for sorts in self.predicates.values():
            for sort in sorts:
                unique_sorts.add(sort)

        unique_sorts = unique_sorts.difference({"BOOLEAN", "REAL", "PREDICATE"})

        for sort in unique_sorts:
            if sort not in self.sorts:
                print("Warning: sort %s is not defined in sorts" % sort)

    def run(self, debug_mode=False):
        """
            run all rules that are inside the rules.py file
        """
        if debug_mode:
            self.show_debug_info()
            # create the pretty table of states
            states_table = PrettyTable()

            # adding the field names of the table
            states_table.field_names = ["Time", "Predicate", "Agent(s)", "Value(s)"]

            self.states[0].show_info(states_table)
        for t in range(1, self.max_t):
            # execute all rules and create all predicates for state t
            for rule in self.rules:
                rule(self.states[:t + 1], t)
            if debug_mode:
                self.states[t].show_info(states_table)
        if debug_mode:
            print("\nThe StateMachine contains the following information per state: ")
            print(states_table)

    
    def filter_nested_predicate_info(self, predicate):
        """
            filters predicate information from a predicate from the scenarios file
        """
        name_predicate = [predicate[0], predicate[1][0]]
        agents = predicate[1][1][:-1]
        values = predicate[1][1][-1]
        return [name_predicate, agents, values]

    @staticmethod
    def filter_predicate_info(predicate):
        """
            filters predicate information from a predicate from the scenarios file
        """
        
        agents = predicate[:-1]
        # value is the last item
        value = predicate[-1]
        return [agents, value]


    def filter_predicate_time(self, time):
        """
            filters predicate duration from a predicate from the scenarios file
            start_time = start_time - 1, since index starts from 0
        """
        if len(time) == 1:
            # just 1 time point
            start_time, end_time = int(time[0]) - 1, int(time[0])
        else:
            # range of time points
            start_time = time[0] - 1
            if time[-1] == INF:
                end_time = self.max_t
            else:
                end_time = int(time[-1])
        return [start_time, end_time]

    def insert_single_predicate(self, predicate, agent, value, start_time, end_time):
        for i in range(start_time, end_time):
            # single predicate
            if predicate in self.states[i].predicates:
                # if the key is already in the dictionary, add a list of the agent + value to the key
                self.states[i].predicates[predicate].append(Predicate(predicate, agent, value))
            else:
                # if the key is not in the dictionary, create a list and add a list of the agent + value to the key
                self.states[i].predicates[predicate] = [Predicate(predicate, agent, value)]

    def insert_nested_predicate(self, nest_name, agent, value, start_time, end_time):
        nested_pred = nest_name[0]
        predicate_name = nest_name[-1]
        to_add_pred = Predicate(predicate_name, agent, value)
        for i in range(start_time, end_time):
            if nested_pred in self.states[i].predicates:
                if predicate_name in self.states[i].predicates[nested_pred]:
                    self.states[i].predicates[nested_pred][predicate_name].append(to_add_pred)
                else:
                    self.states[i].predicates[nested_pred][predicate_name] = [to_add_pred]
            else:
                self.states[i].predicates[nested_pred] = {}
                self.states[i].predicates[nested_pred][predicate_name] = [to_add_pred]

    def insert_predicate(self, predicate, agent, value, start_time, end_time):
        """
            insert the predicate to the corresponding states
        """
        sorts_of_pred = self.predicates[predicate[0]]
        if sorts_of_pred[-1] != "PREDICATE":
            self.insert_single_predicate(predicate[0], agent, value, start_time, end_time)
        else:
            self.insert_nested_predicate(predicate, agent, value, start_time, end_time)