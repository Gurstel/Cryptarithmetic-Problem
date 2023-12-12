# Omar Shalaby
# CS 4613
# Cryptarithmetic Solver

import os
from collections import defaultdict

# This function checks if all variables have been assigned
# and whether those assignments result in a valid solution
# It takes in the original problem and the assignment dictionary
# and returns True if assignment is complete and correct, false otherwise
def is_assignment_complete(assignment, problem):
    # If there are any None values in assignment, we are missing
    # variable assignments
    for key, value in assignment.items():
        if value == None:
            return False
    first_number = ""
    second_number = ""
    third_number = ""
    # Go through the original problem and assign each character it's
    # value in assigned
    for index in range(13):
        if index < 4:
            first_number += assignment[problem[index]]
        elif index < 8:
            second_number += assignment[problem[index]]
        else:
            third_number += assignment[problem[index]]
    return int(first_number) + int(second_number) == int(third_number)


# This function takes in the csp and assignment dictionaries
# and finds the best unassigned variable to select based on
# minimum remaining values and degree heuristics where
# the degree heurisitics is used to break ties by seeing which
# variable has the most constraints
def select_unassigned_variable(csp, assignment):
    unassigned = []
    # Goes through assignment and collects all
    # variables that are so far unassigned
    for key in assignment:
        if assignment[key] is None:
            unassigned.append(key)
    if unassigned == []:
        return None
    count = float("inf")
    mrvs = []
    # For each unassigned variable, see how many values
    # in it's domain are consistent. If it has the most
    # values that are consistent, it sets the precedent
    # for the best variable to choose. If it equals the
    # highest variable, then we add it to the array for degree heuristics
    for var in unassigned:
        var_count = 0
        for val in csp[var]:
            if is_consistent(var, val, assignment.copy()):
                var_count += 1
        if var_count < count:
            mrvs = [var]
            count = var_count
        elif var_count == count:
            mrvs.append(var)

    # If there is only one variable, just return it due to MRV
    if len(mrvs) == 1:
        return mrvs[0]

    selection = ""
    max_constraints = float("-inf")
    # This case is if there are multiple MRV's. We use degree heuristics by
    # finding how many constraints the MRV has. Whichever has the highest number of
    # constraints is our selection
    for mrv in mrvs:
        if csp["constraints"][mrv] > max_constraints:
            selection = mrv
            max_constraints = csp["constraints"][mrv]

    return selection


# This function takes in csp, the variable in question, and assignment
# If the variable is None, simply return an empty array since there are no
# values to check. Otherwise, sort the domain values are return them.
# Noe assignment is not used as a parameter but is included for
# generality of backtracking search
def order_domain_values(csp, var, assignment):
    if var == None:
        return []
    csp[var].sort(reverse=True)
    return csp[var]


# This function takes in a variable, a value, and assignment
# If the variable is an auxillary variable, it is immediately consistent
# since it is not part of the Alldiff constraint.
# Otherwise, it removes the auxillary variables from the assignments,
# assigns the variable the value and returns whether or not
# there exists a duplicate value assigned to multiple variables
def is_consistent(var, val, assignment):
    if var in ["c1", "c2", "c3", "c4"]:
        return True
    assignment[var] = val
    assignment.pop("c1")
    assignment.pop("c2")
    assignment.pop("c3")
    assignment.pop("c4")
    assigned_values = [val for val in assignment.values() if val != None]
    return len(set(assigned_values)) == len(assigned_values)


# This function takes in the csp, assignment, and the problem
# and returns a solution to the cryptarithmetic problem if it
# exists, and None otherwise.
def backtrack(csp, assignment, problem):
    # Checks if we have found a solution
    if is_assignment_complete(assignment, problem):
        return assignment
    var = select_unassigned_variable(csp, assignment)
    # For each value that the variable can take...
    for val in order_domain_values(csp, var, assignment):
        # Checks if that variable is consistent and
        # if so, assign the valueto the variable and
        # recurse with the updated information. If the
        # recurse finds a solution, return it, otherwise
        # clear the assignment.
        if is_consistent(var, val, assignment.copy()):
            assignment[var] = val
            result = backtrack(csp, assignment, problem)
            if result != None:
                return result
            assignment[var] = None
    return None


# This function takes in the input file
# and creates the problem needed to solve. It
# reads in the initial problem and has the hardcoded constraints
# for the specific type of cryptarithmetic problem this program solves.
# It then counts the constraints for each unique variable and sets up their
# domains. It also sets up the assignments starting with each value for each key
# set to None. It returns the problem, the csp, and the assignment
def create_problem(file):
    problem = []
    csp = {}
    csp["constraints"] = defaultdict(int)
    assignment = {}
    with open(file) as f:
        # Goes through each line
        for line in f:
            problem.append(line.replace("\n", ""))
    problem_string = "".join(problem)

    # All the constraints that this specific problem has
    possible_constraints = [
        [3, 7, 12, "c1"],
        [2, 6, 11, "c1", "c2"],
        [1, 5, 10, "c2", "c3"],
        [0, 4, 9, "c3", "c4"],
        [8, "c4"],
    ]
    auxillary = ["c1", "c2", "c3", "c4"]

    # This for-loop goes through each constraint and
    # sees how many unique variables are in that constraint
    # For each unique variable, it increments the number of
    # constraints it has in the csp to identify that it is part
    # of the current constraint
    for constraint in possible_constraints:
        variables_in_constraint = set()
        for variable in constraint:
            var = variable
            if type(variable) != str:
                var = problem_string[variable]
            variables_in_constraint.add(var)
        for variable in variables_in_constraint:
            csp["constraints"][variable] += 1

    # This for-loop increments each non-auxillary variables
    # number of constraints to take in account the Alldiff constraint
    for variable in csp["constraints"]:
        if variable not in auxillary:
            csp["constraints"][variable] += 1

    # This for-loop sets up the domain for all of the given
    # variables that have a domain of {0, 1, 2, ... ,9}
    for index in [1, 2, 3, 5, 6, 7, 9, 10, 11, 12]:
        csp[problem_string[index]] = [str(i) for i in range(10)]

    # This for-loop sets up the domain for all of the given
    # variables that have a domain of {1, 2, ... ,9}
    for index in [0, 4]:
        csp[problem_string[index]] = [str(i) for i in range(1, 10)]

    # This for-loop sets up the domain for all of the auxillary variables
    for constant in auxillary:
        csp[constant] = ["0", "1"]
    # Instead of chaning auxillary, just re-assign c4 the domain of {1}
    csp["c4"] = ["1"]
    csp[problem_string[8]] = ["1"]  # x9 has a domain of {1}

    # This sets up the assignment dictionary by creating a set of the variables
    variables = set(char for char in problem_string)
    # For each constant, add it to the variables
    for constant in auxillary:
        variables.add(constant)

    # For each variable, put it in assignment with value of None
    for variable in variables:
        assignment[variable] = None

    return problem, csp, assignment


# This function creates the output file by taking the file_name,
# the solution, and the initial problem string. It writes to the file
# the associated digit for each character in the intial problem.
def create_output(file_name, solution, initial_problem):
    with open(file_name, "w") as file:
        # Each of these for-loops just indicate which line the
        # digit should be written on in accordance to the specific
        # output required
        for i in range(4):
            file.write(solution[initial_problem[i]])
        file.write("\n")
        for i in range(4, 8):
            file.write(solution[initial_problem[i]])
        file.write("\n")
        for i in range(8, 13):
            file.write(solution[initial_problem[i]])


# Allows users to enter in the text file they want to solve
# if the text file exists. User can type 'quit' to quit the program
# If they type a text file with correct input,
# it will create an output with the solution
def main():
    while True:
        file_name = input("Enter the name of the text file: ")

        if file_name == "quit":
            break
        elif os.path.isfile(file_name):
            problem, csp, assignment = create_problem(file_name)
            solution = backtrack(csp, assignment, "".join(problem))
            create_output("solution_" + file_name, solution, "".join(problem))
        else:
            print("File does not exist. Please enter a valid file name.")


if __name__ == "__main__":
    main()
