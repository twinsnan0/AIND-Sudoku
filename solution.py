# Step frame list
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

    # Find all instances of naked twins
    # Eliminate the naked twins as possibilities for their peers

    # Traverse all units in unit list
    for unit in unitlist:
        # boxes and values in one unit
        unit_boxes = [box for box in unit]
        unit_values = [values[box] for box in unit]
        found_twins_box = []
        # Through all box in one unit
        for i, box in enumerate(unit_boxes):
            # Get the value of box
            value = unit_values[i]
            # if the value's length is 2 and there's two same value in a unit, then we find the twins
            if value not in found_twins_box and len(value) == 2 and unit_values.count(value) == 2:
                # Get the boxes of naked twins
                twins_box = [unit_boxes[x] for x in range(len(unit_values)) if unit_values[x] == value]
                # Get the left boxes except the naked twins in the unit
                checked_boxes = [b for b in unit_boxes if b not in twins_box]
                # Eliminate the twins' value in the left boxes if they have
                for bo in checked_boxes:
                    if len(values[bo]) > 1:
                        assign_value(values, bo, values[bo].replace(value[0], ''))
                        assign_value(values, bo, values[bo].replace(value[1], ''))
                found_twins_box += twins_box

    return values


def cross(a, b):
    """Cross product of elements in A and elements in B."""
    return [s + t for s in a for t in b]


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
    values = []
    all_digits = '123456789'
    for c in grid:
        if c == '.':
            values.append(all_digits)
        elif c in all_digits:
            values.append(c)
    assert len(values) == 81
    return dict(zip(boxes, values))


def display(values):
    """
    Display the values as a 2-D grid.
    Args:
        values(dict): The sudoku in dictionary form
    """
    width = 1 + max(len(values[s]) for s in boxes)
    line = '+'.join(['-' * (width * 3)] * 3)
    for r in rows:
        print(''.join(values[r + c].center(width) + ('|' if c in '36' else '')
                      for c in cols))
        if r in 'CF':
            print(line)
    return


def eliminate(values):
    """
    Eliminate values from peers of each box with a single value.

    Go through all the boxes, and whenever there is a box with a single value,
    eliminate this value from the set of values of all its peers.

    Args:
        values: Sudoku in dictionary form.
    Returns:
        Resulting Sudoku in dictionary form after eliminating values.
    """

    # Get all the solved values with fixed value
    solved_boxes = [box for box in values.keys() if len(values[box]) == 1]
    # Go through all the boxes
    for box in solved_boxes:
        value = values[box]
        # Eliminate this value from the set of values of all its peers.
        for peer in peers[box]:
            assign_value(values, peer, values[peer].replace(value, ''))
    return values


def only_choice(values):
    """
    Finalize all values that are the only choice for a unit.

    Go through all the units, and whenever there is a unit with a value
    that only fits in one box, assign the value to this box.

    Input: Sudoku in dictionary form.
    Output: Resulting Sudoku in dictionary form after filling in only choices.
    """
    # Go through the unit
    for unit in unitlist:
        for digit in '123456789':
            # if only one box has the digit, then assign the digit to it
            dplaces = [box for box in unit if digit in values[box]]
            if len(dplaces) == 1:
                assign_value(values, dplaces[0], digit)
    return values


def reduce_puzzle(values):
    """
    Iterate eliminate() and only_choice(). If at some point, there is a box with no available values, return False.
    If the sudoku is solved, return the sudoku.
    If after an iteration of both functions, the sudoku remains the same, return the sudoku.
    Input: A sudoku in dictionary form.
    Output: The resulting sudoku in dictionary form.
    """
    stalled = False
    while not stalled:
        # Check how many boxes have a determined value
        solved_values_before = len([box for box in values.keys() if len(values[box]) == 1])
        # Use the Eliminate Strategy
        values = eliminate(values)
        # Use the Only Choice Strategy
        values = only_choice(values)
        # Use the Naked Twins Strategy
        values = naked_twins(values)
        # Check how many boxes have a determined value, to compare
        solved_values_after = len([box for box in values.keys() if len(values[box]) == 1])
        # If no new values were added, stop the loop.
        stalled = solved_values_before == solved_values_after
        # Sanity check, return False if there is a box with zero available values:
        if len([box for box in values.keys() if len(values[box]) == 0]):
            return False
    return values
    pass


def search(values):
    """
    Using depth-first search and propagation, try all possible values.
    """
    values = reduce_puzzle(values)
    if values is False:
        # Failed earlier
        return False
    if all(len(values[s]) == 1 for s in boxes):
        # Solved!
        return values
    # Choose one of the unfilled squares with the fewest possibilities
    n, s = min((len(values[s]), s) for s in boxes if len(values[s]) > 1)
    # Now use recurrence to solve each one of the resulting sudokus, and return new values if solved
    for value in values[s]:
        new_sudoku = values.copy()
        assign_value(new_sudoku, s, value)
        attempt = search(new_sudoku)
        if attempt:
            return attempt


def solve(grid):
    """
    Find the solution to a Sudoku grid.
    Args:
        grid(string): a string representing a sudoku grid.
            Example: '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    Returns:
        The dictionary representation of the final sudoku grid. False if no solution exists.
    """
    # Init the values at first
    values = grid_values(grid)
    # get resolved values after depth-first search
    result = search(values)
    # If false, Can not solve the sudoku puzzle
    if result is False:
        print("Can not solve the sudoku puzzle")
        return values
    # Return the final solved values
    else:
        return result


# Define the labels of the the boxes, using ABCDEFGHI as the row labels, 123456780 as the col labels
rows = 'ABCDEFGHI'
cols = '123456789'
boxes = cross(rows, cols)

# Find all sudoku units in a diagonal sudoku.
# Units has row_units, column_units, square_units and cross_units.
row_units = [cross(r, cols) for r in rows]
column_units = [cross(rows, c) for c in cols]
square_units = [cross(rs, cs) for rs in ('ABC', 'DEF', 'GHI') for cs in ('123', '456', '789')]
cross_units = [[rows[i] + cols[i] for i in range(9)], [rows[i] + cols[-i - 1] for i in range(9)]]
unitlist = row_units + column_units + square_units + cross_units
# Find all units that are related to each box
units = dict((s, [u for u in unitlist if s in u]) for s in boxes)
peers = dict((s, set(sum(units[s], [])) - {s}) for s in boxes)

if __name__ == '__main__':
    # Input string of sudoku
    # diag_sudoku_grid = '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    diag_sudoku_grid = '9.1....8.8.5.7..4.2.4....6...7......5..............83.3..6......9................'
    # Solve and display on the console
    display(solve(diag_sudoku_grid))
    # Display in the pygame.
    try:
        from visualize import visualize_assignments

        visualize_assignments(assignments)
    except SystemExit:
        pass
    except Exception:
        print('We could not visualize your board due to a pygame issue. Not a problem! It is not a requirement.')
