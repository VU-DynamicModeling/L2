""" visualization.py
     for visualization
    """
from matplotlib import lines

import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import matplotlib.patches as mpatches

import random
import itertools
import numpy as np

random.seed(42)
np.random.seed(42)


def make_visualization_dic(state_machine):
    visualization_dic = {}
    for state in state_machine.states:
        t = state.t
        predicates = state.predicates
        for predicate_name in predicates:
            predicate = predicates[predicate_name]
            if type(predicate) != dict:
                # non-nested predicate
                visualization_dic = add_non_nested_predicate(predicate, predicate_name, visualization_dic, t)
            else:
                # nested predicate
                nested_predicates = predicates[predicate_name]
                for nested_predicate_name in nested_predicates:
                    nested_predicate = nested_predicates[nested_predicate_name]
                    nested_predicate_name = "%s_%s" % (predicate_name, nested_predicate_name)
                    visualization_dic = add_non_nested_predicate(nested_predicate, nested_predicate_name,
                                                                 visualization_dic, t)

    return visualization_dic


def add_non_nested_predicate(predicate, predicate_name, visualization_dic, t):
    for predicate_values in predicate:
        agent = tuple(predicate_values.agents) if len(predicate_values.agents) > 1 else predicate_values.agents[
            0]
        value = predicate_values.value
        visualization_dic = add_predicate_visualization(agent, value, predicate_name, visualization_dic, t)
    return visualization_dic


def add_predicate_visualization(agent, value, predicate_name, visual_dic, t):
    if predicate_name in visual_dic:
        if agent in visual_dic[predicate_name]:
            visual_dic[predicate_name][agent].append((t, value))
        else:
            visual_dic[predicate_name][agent] = [(t, value)]
    else:
        visual_dic[predicate_name] = {}
        visual_dic[predicate_name][agent] = [(t, value)]
    return visual_dic


def check_completeness(visual_dic, StateMachine):
    for predicate_name in visual_dic.keys():
        predicate = visual_dic[predicate_name]
        for agent in predicate.keys():
            for i in range(0, StateMachine.max_t):
                t1 = i + 1
                if i == len(visual_dic[predicate_name][agent]):
                    visual_dic[predicate_name][agent].append((t1, None))
                t2 = visual_dic[predicate_name][agent][i][0]
                if t1 != t2:
                    visual_dic[predicate_name][agent].insert(i, (t1, None))
    return visual_dic


def retrieve_nested_sort(StateMachine, nested_pred):
    for agent in nested_pred:
        predicate_info = nested_pred[agent]
        all_values = [t_and_value[1] for t_and_value in predicate_info]
        if type(all_values[0]) != list:
            unique_values = list(set([value for value in all_values if value != None]))
            for sort in StateMachine.sorts:
                if all(value in StateMachine.sorts[sort] for value in unique_values):
                    return sort
            if type(unique_values[0]) == bool:
                return "BOOLEAN"
            else:
                return "REAL"
        else:
            merged = list(itertools.chain(*all_values))
            unique_values = list(set([value for value in merged if value != None]))
            combinations = []
            for unique_value in unique_values:
                for sort in StateMachine.sorts:
                    if unique_value in StateMachine.sorts[sort]:
                        if sort not in combinations:
                            combinations.append(sort)
                        break
                if type(unique_value) == bool and "BOOLEAN" not in combinations:
                    combinations.append("BOOLEAN")
                elif type(unique_value) == float and "REAL" not in combinations:
                    combinations.append("REAL")
            return combinations


def make_type_of_plot_dic(StateMachine, visualization_dic):
    type_of_plot_dic = {}
    for predicate in visualization_dic:
        if predicate in StateMachine.predicates:
            type_of_plot_dic[predicate] = StateMachine.predicates[predicate][-1]
        else:
            nested_pred = visualization_dic[predicate]
            nested_sort = retrieve_nested_sort(StateMachine, nested_pred)
            type_of_plot_dic[predicate] = nested_sort
    return type_of_plot_dic


def make_numerical_plot(predicate_name, predicates):
    line_styles = ['solid', '--', '-.', '-']
    y_min = 0
    y_max = 1
    line_style = 0

    for predicate in predicates:
        t, values = zip(*predicates[predicate])
        y_min_temp = min(y for y in values if y is not None)
        y_min = y_min_temp if y_min_temp < y_min else y_min
        y_max_temp = max(y for y in values if y is not None)
        y_max = y_max_temp if y_max_temp > y_max else y_max
        plt.plot(t, values, label=predicate, linestyle=line_styles[line_style])
        line_style += 1
    plt.title("Predicates of predicate \"%s\"" % predicate_name)
    plt.legend()
    plt.ylim([y_min - 0.01, y_max + y_max / 20])
    plt.yticks(np.linspace(y_min, y_max, 10))
    plt.grid(True)
    plt.show()


def make_bar_plot(predicate_name, predicates, sort, sorts):
    color = ["lightgray"]
    if not sort and not sorts:
        possibilities = [True, False]
        color.extend([(0, 0, 1.0), (1.0, 0, 0)])
    else:
        possibilities = sorts[sort].copy()
        for _ in range(len(possibilities)):
            # create a random rgb
            color.append((random.random(), random.random(), random.random()))
    possibilities.insert(0, None)
    result_matrix = []
    names = []
    for predicate in predicates:
        names.append(predicate + "\n")
        _, values = zip(*predicates[predicate])
        row = [possibilities.index(value) for value in values]
        result_matrix.append(row)
    legend_possibilities = possibilities
    legend_colors = color
    # if there is no None, but still grey color in the cmap --> delete it (else bug)
    if not(any(0 in row for row in result_matrix)):
        color.pop(0)
        possibilities.pop(0)
        if len(np.unique(np.array(result_matrix).squeeze())) == 1:
            possibilities = [possibilities[np.array(result_matrix).squeeze()[0] - 1]]
            color = [color[np.array(result_matrix).squeeze()[0] - 1]]
    # Hardcoded but fixed the True False bug...
    elif possibilities == [None, True, False] and len(np.unique(np.array(result_matrix).squeeze())) == 2:
        items = np.unique(np.array(result_matrix).squeeze())
        possibilities = [possibilities[i] for i in items]
        color = [color[i] for i in items]
    color_dict = {str(possibilities[i]) : color[i] for i in range(0, len(possibilities))}
    legend_color_dict = {str(legend_possibilities[i]) : legend_colors[i] for i in range(0, len(legend_possibilities))}
    cmap = ListedColormap(color)
    matfig = plt.figure(figsize=(8,8))

    plt.matshow(result_matrix, cmap=cmap, fignum=matfig.number)
    plt.xlabel("Time Steps")
    # show the x labels
    plt.xticks(np.arange(-0.5, len(result_matrix[0]), step=1), ha="right", labels=range(len(result_matrix[0]) + 1))
    # show the y labels
    plt.yticks(np.arange(len(names)), names)
    plt.legend(legend_color_dict)
    # make a clear grid
    for i in range(len(names)):
        plt.axhline(i + 0.5, color='k')
    plt.grid(axis='x', color='k', linewidth=2)
    plt.title("Predicates of predicate \"%s\"" % predicate_name)
    patches = []
    for key in legend_color_dict:
        patch = mpatches.Patch(color=legend_color_dict[key], label=key)
        patches.append(patch)
    plt.legend(handles=patches, bbox_to_anchor=(1.01, 1), loc='upper left', borderaxespad=0)
    fig = plt.gcf()
    fig.set_size_inches(25.5, len(names) * 2.2) if len(names) > 1 else fig.set_size_inches(25.5, 4)
    plt.show()


def make_bar_plot_list(predicate_name, predicates):
    color = ["lightgray"]
    combinations = [predicates[agent] for agent in predicates]
    combinations = list(itertools.chain.from_iterable(combinations))
    combinations = [combination[1] for combination in combinations]
    possibilities = [list(x) for x in set(tuple(x) for x in combinations)]
    for _ in range(len(possibilities)):
        # create a random rgb
        color.append((random.random(), random.random(), random.random()))
    possibilities.insert(0, None)
    result_matrix = []
    names = []
    for predicate in predicates:
        names.append(predicate + "\n")
        _, values = zip(*predicates[predicate])
        row = [possibilities.index(value) for value in values]
        result_matrix.append(row)
    # if there is no None, but still grey color in the cmap --> delete it (else bug)
    if not(any(0 in row for row in result_matrix)):
        color.pop(0)
        possibilities.pop(0)
    color_dict = {", ".join(possibilities[i]) : color[i] for i in range(0, len(possibilities))}
    cmap = ListedColormap(color)
    matfig = plt.figure(figsize=(8,8))
    plt.matshow(result_matrix, cmap=cmap, fignum=matfig.number)
    plt.xlabel("Time Steps")
    # show the x labels
    plt.xticks(np.arange(-0.5, len(result_matrix[0]), step=1), ha="right", labels=range(len(result_matrix[0]) + 1))
    # show the y labels
    plt.yticks(np.arange(len(names)), names)
    plt.legend(labels=possibilities)
    # make a clear grid
    for i in range(len(names)):
        plt.axhline(i + 0.5, color='k')
    plt.grid(axis='x', color='k', linewidth=2)
    plt.title("Predicates of predicate \"%s\"" % predicate_name)
    patches = []
    for key in color_dict:
        patch = mpatches.Patch(color=color_dict[key], label=key)
        patches.append(patch)
    plt.legend(handles=patches, bbox_to_anchor=(1., 1), loc='upper left', borderaxespad=0, prop={'size': 9})
    fig = plt.gcf()
    fig.set_size_inches(25.5, len(names) * 2.2) if len(names) > 1 else fig.set_size_inches(25.5, 4)
    plt.show()

def visualize(visualization_dic, type_of_plot_dic, sorts):
    for predicate in type_of_plot_dic:
        # numerical plot
        if type_of_plot_dic[predicate] == "REAL":
            make_numerical_plot(predicate, visualization_dic[predicate])
        elif type(type_of_plot_dic[predicate]) == list:
            make_bar_plot_list(predicate, visualization_dic[predicate])
        elif type_of_plot_dic[predicate] == "BOOLEAN":
            make_bar_plot(predicate, visualization_dic[predicate], False, False)
        else:
            make_bar_plot(predicate, visualization_dic[predicate], type_of_plot_dic[predicate], sorts)


def run_visualization(StateMachine, predicate_to_remove=None):
    """"
    Creates the visualization of every predicate that is inside the StateMachine.
    "predicate_to_remove" is a list containing the predicates that should not be plotted.
    """
    if predicate_to_remove is None:
        predicate_to_remove = []
    visualization_dic = make_visualization_dic(StateMachine)
    visualization_dic = check_completeness(visualization_dic, StateMachine)
    type_of_plot_dic = make_type_of_plot_dic(StateMachine, visualization_dic)
    for predicate in predicate_to_remove:
        if predicate not in visualization_dic:
            print("Warning: the predicate does not seem to be available in the states")
            break
        del visualization_dic[predicate]
        if predicate not in type_of_plot_dic:
            print("Warning: the predicate does not seem to be available in the predicates file")
            break
        del type_of_plot_dic[predicate]
    print("The following predicates will be visualized:")
    for predicate in visualization_dic:
        print(predicate)
    visualize(visualization_dic, type_of_plot_dic, StateMachine.sorts)