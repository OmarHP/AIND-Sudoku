assignments = []

def assign_value(values, box, value):
    """
    Please use this function to update your values dictionary!
    Assigns a value to a given box. If it updates the board record it.
    """

    # Don't waste memory appending actions that don't actually change any values
    if values[box] == value:
        return values

    values[box] = value
    if len(value) == 1:
        assignments.append(values.copy())
    return values

def naked_twins(values):
    """Eliminate values using the naked twins strategy.
    Args:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}

    Returns:
        the values dictionary with the naked twins eliminated from peers.
    """

    # Run naked twins algorithm for each unit
    for unit in UNIT_LIST:
        twins = dict()
        # For each box in unit, checks if it could be a twin
        for box in unit:
            # if values length equals two, it might have a twin
            if len(values[box]) == 2:
                # Add box to twins dictionary using its values string as key
                twins.setdefault(values[box], []).append(box)
   
        # For each pair of twins found
        for v, tb in twins.items(): # v: length-two set of values, tb: twin boxes
            # finding more than a couple of twins for each length-two set, means one of them cannot be asigned
            #if len(tb) > 2:
            #    return False
            if len(tb) == 2:
                # Remove twin values from same-unit peers
                for box in unit:
                    if box not in tb:
                        assign_value(values, box, values[box].replace(v[0], ''))
                        assign_value(values, box, values[box].replace(v[1], ''))
    return values

def cross(A, B):
    "Cross product of elements in A and elements in B."
    return [a+b for a in A for b in B]

def grid_values(grid):
    """
    Convert grid into a dict of {square: char} with '123456789' for empties.
    Args:
        grid(string) - A grid in string form.
    Returns:
        A grid in dictionary form
            Keys: The boxes, e.g., 'A1'
            Values: The value in each box, e.g., '8'. If the box has no value, then the value will be '123456789'.
    """
    chars = []
    for c in grid:
        if c in DIGITS:
            chars.append(c)
        elif c == '.':
            chars.append(DIGITS)
    assert len(chars) == 81
    return dict(zip(BOXES, chars))

def display(values):
    """
    Display the values as a 2-D grid.
    Args:
        values(dict): The sudoku in dictionary form
    """
    width = 1+max(len(values[s]) for s in BOXES)
    line = '+'.join(['-'*(width*3)]*3)
    for r in ROWS:
        print(''.join(values[r+c].center(width)+('|' if c in '36' else '')
                      for c in COLS))
        if r in 'CF': 
            print(line)
    return

def eliminate(values):
    """Eliminate values from peers of each box with a single value.

    Go through all the boxes, and whenever there is a box with a single value,
    eliminate this value from the set of values of all its peers.

    Args:
        values: Sudoku in dictionary form.
    Returns:
        Resulting Sudoku in dictionary form after eliminating values.
    """
    for key in values.keys():
        if len(values[key]) == 1:
            for peer in PEERS[key]:
                value = values[peer].replace(values[key], '')
                assign_value(values, peer, value )
    return values

def only_choice(values):
    """
    Finalize all values that are the only choice for a unit.

    Go through all the units, and whenever there is a unit with a value
    that only fits in one box, assign the value to this box.

    Args:
        values: Sudoku in dictionary form..
    Return: 
        Resulting Sudoku in dictionary form after filling in only choices.
    """
    for unit in UNIT_LIST:
        for digit in DIGITS:
            reps = [box for box in unit if digit in values[box]]
            if len(reps) == 1:
                assign_value(values, reps[0], digit)
    return values


def reduce_puzzle(values):
    """
    Iterate eliminate(), only_choice() and naked_twins(). If at some point, there is a box with no available values, return False.

    If the sudoku is solved, return the sudoku.

    If after an iteration of the three functions, the sudoku remains the same, return the sudoku.

    Args:
        values: Sudoku in dictionary form.
    Return:
        The resulting sudoku in dictionary form.
    """
    stalled = False
    while not stalled:
        # Check how many boxes have only one possible value
        solved_values_before = len([box for box in values.keys() if len(values[box]) == 1])
        # Use the Eliminate Strategy
        eliminate(values)
        # Use the Only Choice Strategy
        only_choice(values)
        # Use the Naked Twins Strategy
        naked_twins(values)
        # Check how many boxes now have only one possible value, to compare
        solved_values_after = len([box for box in values.keys() if len(values[box]) == 1])
        #if no new values were addes, stop the loop
        stalled = solved_values_before == solved_values_after
        # Sanity check, return False if there is a box with zero available values:
        if len([box for box in values.keys() if len(values[box]) == 0]):
            return False
    return values

def search(values):
    """
    Using depth-first search and propagation, create a search tree and solve the sudoku.

    Args:
        values: Sudoku in dictionary form.
    Return:
        The resulting sudoku in dictionary form.
    """

    # First, reduce the puzzle using the reduce_puzzle function
    values = reduce_puzzle(values)

    # Check if something went wrong
    if values is False:
        return False ##Failed earlier

    # Find all boxes with more than one possible value
    unfilled_squares = [box for box in values.keys() if len(values[box]) > 1]

    # If no box have more than one possible solution, it's done, a solution has been found
    if len(unfilled_squares) == 0:
        return values

    # Choose one of the unfilled squares with the fewest possibilities
    length, box = min((len(values[box]), box) for box in unfilled_squares)

     # Now use recursion to solve each one of the resulting sudokus, and if one returns a value (not False), return that answer!
    for digit in values[box]:
        new_values = values.copy()
        assign_value(new_values, box, digit)
        attempt = search(new_values)
        if attempt:
            return attempt
    # If no solution was found
    return False


def solve(grid):
    """
    Find the solution to a Sudoku grid.
    Args:
        grid(string): a string representing a sudoku grid.
            Example: '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    Returns:
        The dictionary representation of the final sudoku grid. False if no solution exists.
    """
    return search(grid_values(grid))
    


ROWS = "ABCDEFGHI"
COLS = "123456789"
DIGITS = "123456789"

BOXES = cross(ROWS, COLS)
ROW_UNITS = [cross(row, COLS) for row in ROWS]
COLUM_UNITS = [cross(ROWS, col) for col in COLS]
SQUARE_UNITS = [cross(rowSet, colSet) for rowSet in ["ABC", "DEF", "GHI"] for colSet in ["123", "456", "789"]]
# Add diagonal units to support diagonal sudoku restrictions
DIAGONAL_UNITS = [[ROWS[i]+COLS[i] for i in range(9)], [ROWS[8-i]+COLS[i] for i in range(9)]]

UNIT_LIST = ROW_UNITS + COLUM_UNITS + SQUARE_UNITS +DIAGONAL_UNITS
UNITS = dict((key, [unit for unit in UNIT_LIST if key in unit]) for key in BOXES)
PEERS = dict((key, set([item for sublist in UNITS[key] for item in sublist])- set([key])) for key in BOXES)


if __name__ == '__main__':
    diag_sudoku_grid = '9.1....8.8.5.7..4.2.4....6...7......5..............83.3..6......9................'
    display(solve(diag_sudoku_grid))

    try:
        from visualize import visualize_assignments
        visualize_assignments(assignments)

    except SystemExit:
        pass
    except:
        print('We could not visualize your board due to a pygame issue. Not a problem! It is not a requirement.')
