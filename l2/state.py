""" state.py
    Contains the information of a state at a certain times tep
    """
import inspect

class State:
    def __init__(self, t, possible_predicates, sorts):
        """
            t = time step of the state
            predicates = a dictionary containing the predicates of the state
        """
        self.t = t
        self.predicates = {}
        self.possible_predicates = possible_predicates
        self.sorts = sorts

    def __str__(self):
        return f"State {self.t}: {self.predicates}"

    def __repr__(self) -> str:
        p = "\n".join(self.predicates)
        return f"State {self.t}: {p}"

    def check_predicate(self, predicate):
        """
            checks whether a predicate exists within this state
        """
        return predicate in self.predicates

    def get_predicate(self, predicate):
        """
            returns the predicate (list of agent(s) with corresponding value(s)) of this state
        """
        if predicate in self.predicates:
            return self.predicates[predicate]
        else:
            print("The predicate \"%s\" is not found in the state with time %d" % (predicate, self.t))
            print("The possible predicates in the state with time %d are: " % self.t, end="")
            print(", ".join(self.predicates))
            return []

    def get_predicate_by_agent(self, predicate, agent, index=0):
        """
        returns a list of all predicate entries with a certain agent at the given index
        """
        if self.get_predicate(predicate) != []:
            output = []
            for entry in self.predicates[predicate]:
                if agent == entry.agents[index]:
                    output.append(entry)
            if self.get_predicate(predicate) != []:
                return output
            else:
                print("Warning: The predicate \"%s\", with agent \"%s\", on index \"%d\", is not found in the state with time %d" % (predicate, agent, index, self.t))
                print("Please check the spelling of the predicate and the agent, or the index, or use the debug function")
                return []
        else:
            print("Warning: The predicate \"%s\" is not found in the state with time %d" % (predicate, self.t))
            print("The possible predicates in the state with time %d are: " % self.t, end="")
            print(", ".join(self.predicates))
            return []


    def get_single_predicate_by_agent(self, predicate, agent, index=0):
        """
        returns a list of all predicate entries with a certain agent at the given index
        """
        if self.get_predicate(predicate) != []:
            output = []
            for entry in self.predicates[predicate]:
                if agent == entry.agents[index]:
                    output.append(entry)
            if self.get_predicate(predicate) != []:
                if len(output) > 1:
                    print("Warning: The predicate \"%s\", with agent \"%s\", on index \"%d\", is found multiple times in the state with time %d" % (predicate, agent, index, self.t))
                    print("If this is your intention, please use the get_predicate_by_agent function instead of the get_single_predicate_by_agent function")
                return output[0]
            else:
                print("Warning: The predicate \"%s\", with agent \"%s\", on index \"%d\", is not found in the state with time %d" % (predicate, agent, index, self.t))
                print("Please check the spelling of the predicate and the agent, or the index, or use the debug function")
                return []
        else:
            print("Warning: The predicate \"%s\" is not found in the state with time %d" % (predicate, self.t))
            print("The possible predicates in the state with time %d are: " % self.t, end="")
            print(", ".join(self.predicates))
            return []


    def check_validity_pred(self, predicate_name, agent, value, func_name):
        """
            check the validity of the predicate, based on the predicate name and the sorts
        """
        if predicate_name not in self.possible_predicates:
            print("The predicate \"%s\" is not a valid predicate, at state with time %d. This error is caused by "
                  "rule: %s" % (predicate_name, self.t, func_name))
            print("The valid predicates are: ", end="")
            print(", ".join(self.possible_predicates))
            return False
        sorts_of_pred = self.possible_predicates[predicate_name]
        # check validity agents
        for i in range(len(agent)):
            if sorts_of_pred[i] != "AGENT":
                print("Expected sort: AGENT, got sort: sort %s, for predicate %s on place %d, at state with time %d. "
                      "This error is caused by rule: %s" % (sorts_of_pred[i], predicate_name, i + 1, self.t, func_name))
                return False
            elif agent[i] not in self.sorts[sorts_of_pred[i]]:
                print("Agent %s does not seem to exist in the AGENT sorts, at state with time %d. This error is caused "
                      "by rule: %s" % (agent[i], self.t, func_name))
                return False
        # check validity value of the sort
        if sorts_of_pred[-1] == "BOOLEAN":
            if type(value) != bool:
                print("Expected sort: BOOLEAN, got a different sort (with value %s), for predicate %s, at state with "
                      "time %d. This error is caused by rule: %s" % (value, predicate_name, self.t, func_name))
                return False
        elif sorts_of_pred[-1] == "REAL":
            if not ((type(value) == int) ^ (type(value) == float)):
                print("Expected sort: REAL, got a different sort (with value %s), for predicate %s, at state with "
                      "time %d. This error is caused by rule: %s" %(value, predicate_name, self.t, func_name))
                return False
        elif value not in self.sorts[sorts_of_pred[-1]]:
            print("Expected sort: %s, got a different sort (with value %s), for predicate %s, at state with time %d. "
                  "This error is caused by rule: %s" % (sorts_of_pred[-1], value, predicate_name, self.t, func_name))
            print("The possible values for sort %s are: " % sorts_of_pred[-1], end="")
            print(", ".join(self.sorts[sorts_of_pred[-1]]))
            return False
        return True

    def add_predicate_to_state(self, predicate):
        """
        adds a predicate to a state
        """
        if self.check_validity_pred(predicate.name, predicate.agents, predicate.value, inspect.stack()[1][3]):
            # the predicate (name) already exists in the state
            if predicate.name in self.predicates:
                # only add the predicate to the list
                self.predicates[predicate.name].append(predicate)
            else:
                self.predicates[predicate.name] = [predicate]

    def add_nested_predicate_to_state(self, nest_name, predicate_name, predicate):
        """
        adds a nested predicate to a state (predicate_name predicate under the nest_name predicate)
        """
        if nest_name in self.predicates:
            if predicate_name in self.predicates[nest_name]:
                self.predicates[nest_name][predicate_name].append(predicate)
            else:
                self.predicates[nest_name][predicate_name] = [predicate]
        else:
            self.predicates[nest_name] = {}
            self.predicates[nest_name][predicate_name] = [predicate]

    def retrieve_observations(self):
        """
        retrieves all observations of a state
        """
        if "observed" in self.predicates:
            return self.predicates["observed"]
        else:
            return False

    def retrieve_beliefs(self):
        """
        retrieves all beliefs of a state
        """
        if "belief" in self.predicates:
            return self.predicates["belief"]
        else:
            return False

    def retrieve_assessments(self):
        """
        retrieves all assessments of a state
        """
        if "assessment" in self.predicates:
            return self.predicates["assessment"].value
        else:
            return False

    def get_nested_predicate(self, nest_name, pred_name):
        """
        retrieve a nested predicate from a state (predicate_name predicate under the nest_name predicate)
        """
        if nest_name in self.predicates:
            if pred_name in self.predicates[nest_name]:
                return self.predicates[nest_name][pred_name]
            else:
                print("The predicate \"%s\" does not seem to exist in the \"%s\" predicate in state with time %d." % (pred_name, nest_name, self.t))
                print("The possible nested predicates for \"%s\" are: " % nest_name)
                for pred in self.predicates[nest_name]:
                    print("%s %s" % (nest_name, pred))
        else:
            print("\"%s\" does not seem to exist in state with time %d." % (pred_name, self.t))
            return []

    def get_nested_predicate_by_name(self, nest, predicate_name, agent, index=0):
        """
        retrieve a nested predicate from a state by agent name (predicate_name predicate under the nest_name predicate)
        """
        if predicate_name in self.predicates[nest]:
            output = []
            for entry in self.predicates[nest][predicate_name]:
                if agent == entry.agents[index]:
                    output.append(entry)
            return output
        else:
            print("No nested %s predicate of %s at time %d with agent %s" % (nest, predicate_name, self.t, agent))
            return []

    def check_belief_in_beliefs(self, predicate_name):
        """
        checks whether a belief is in the beliefs of a state
        """
        return predicate_name in self.predicates["belief"].value

    def check_nested_pred(self, nest_name, pred_name):
        """
        checks whether there are predicates with pred_name in the overarching predicate with name nest_name
        """
        if nest_name in self.predicates:
            if pred_name in self.predicates[nest_name]:
                return True
        return False

    def show_info(self, table):
        """
        add info to the states table
        """
        first_t = True
        for predicate in self.predicates:
            first_pred = True
            if type(self.predicates[predicate]) != dict:
                for predicate_info in self.predicates[predicate]:
                    values = ", ".join(predicate_info.value.copy()) if type(predicate_info.value) == list else predicate_info.value
                    if first_pred:
                        if first_t:
                            table.add_row([self.t, predicate_info.name, ", ".join(predicate_info.agents), values])
                            first_t, first_pred = False, False
                        else:
                            table.add_row(["", predicate_info.name, ", ".join(predicate_info.agents), values])
                            first_pred = False
                    else:
                        table.add_row(["", "", ", ".join(predicate_info.agents), values])
            else:
                for nested_pred in self.predicates[predicate]:
                    first_pred = True
                    for predicate_info in self.predicates[predicate][nested_pred]:
                        values = ", ".join(predicate_info.value.copy()) if type(predicate_info.value) == list else predicate_info.value
                        if first_pred:
                            if first_t:
                                table.add_row([self.t, predicate + ": " + predicate_info.name, ", ".join(predicate_info.agents), values])
                                first_t, first_pred = False, False
                            else:
                                table.add_row(["", predicate + ": " + predicate_info.name, ", ".join(predicate_info.agents), values])
                                first_pred = False
                        else:
                            table.add_row(["", "", ", ".join(predicate_info.agents), values])


class Predicate:
    def __init__(self, name, agents, value):
        self.name = name
        self.agents = agents
        self.value = value

    def get_name_agent(self, index=0):
        try:
            return self.agents[index]
        except IndexError:
            print("The number of agents of this predicate is: %d, while you asked for agent %d"
                  % (len(self.agents), index))

    def get_value(self):
        return self.value

    def print(self):
        return str(self.agents) + str(self.value)
    
    def __str__(self):
        return f"{self.name}({', '.join(self.agents)}) = {self.value}"
    
    def __iter__(self):
        return iter(self.agents + [self.value])
    
