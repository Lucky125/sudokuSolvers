import sys

SOLVE_METHODS = [
    ('NAIVE', 'naive solution'),
    ('BACKTRACK', 'backtracking'),
    ('LEAST_POSSIBILITIES', 'backtracking with least posibilities'),
    ('WITH_FORCE', 'backtracking with forced choices'),
]

#Checks if a row has at most one of each number.
def check_row(sudoku, row):
    found = set()
    for i in range(9):
        val = sudoku[row*9 + i]
        if (val != '.'):
            if val in found:
                return False
            found.add(val)
    return True

#Checks if a column has at most one of each number.
def check_col(sudoku, col):
    found = set()
    for i in range(9):
        val = sudoku[col + i*9]
        if (val != '.'):
            if val in found:
                return False
            found.add(val)
    return True

#Checks if a box has at most one of each number.
def check_box(sudoku, box_row, box_col):
    found = set()
    for i in range(3):
        for j in range(3):
            val = sudoku[(box_row*3+j)*9+(box_col*3+i)]
            if (val != '.'):
                if val in found:
                    return False
                found.add(val)
    return True

#Returns a list of sudoku grid errors.
def is_valid_with_errors(sudoku):
    errors = []
    for i in range(9):
        if not check_row(sudoku,i):
            errors.append(('row',i))
    for j in range(9):
        if not check_col(sudoku,j):
            errors.append(('col',i))
    for i in range(3):
        for j in range(3):
            if not check_box(sudoku, i, j):
                errors.append(('box',i,j))
    return errors

#Returns true if the sudoku grid has no errors.
def is_valid(sudoku):
    errors = []
    for i in range(9):
        if not check_row(sudoku,i):
            return False
    for j in range(9):
        if not check_col(sudoku,j):
            return False
    for i in range(3):
        for j in range(3):
            if not check_box(sudoku, i, j):
                return False
    return True

#Returns true if the value at an index doesn't violate the grid
def validate_index(sudoku, index):
    return check_row(sudoku, index // 9) \
        and check_col(sudoku, index % 9) \
        and check_box(sudoku, index // 27, (index % 9) // 3)

def poslistcount_creator():
    poslistcount = [[[set() for _ in range(9)] for _ in range(9)] for _ in range(3)]
    for i in range(81):
        for j in range(9):
            poslistcount[0][i//9][j].add(i)
            poslistcount[1][i%9][j].add(i)
            poslistcount[2][(i//27)*3+((i%9)//3)][j].add(i)
    return poslistcount

#Main solve method
def solve(sudoku, solve_type, early_exit = None):
    if (solve_type == 'NAIVE'):
        return naive_solve(sudoku, early_exit)

    if (solve_type == 'BACKTRACK'):
        return backtrack_solve(sudoku, early_exit)

    poslist = [['.']*9 for _ in range(81)]

    if (solve_type == 'LEAST_POSSIBILITIES'):
        for i in range(81):
            if (sudoku[i] != '.'):
                prune(i, int(sudoku[i]), poslist)
        return least_possibilities_solve(sudoku, poslist, early_exit)

    poslistcount = poslistcount_creator()

    if (solve_type == 'WITH_FORCE'):
        for i in range(81):
            if (sudoku[i] != '.'):
                count_prune(i,int(sudoku[i]),poslist, poslistcount)
        return with_force_solve(sudoku, poslist, poslistcount, early_exit)

def naive_solve(sudoku, early_exit = None):
    if (early_exit != None and early_exit.is_set()):
        sys.exit()
    try:
        i = sudoku.index('.')
    except ValueError:
        #The grid is full, so we check if we have a valid grid.
        return is_valid(sudoku)

    for n in range(1,10):
        sudoku[i] = str(n)
        if (naive_solve(sudoku, early_exit)):
            return True
    sudoku[i] = '.'
    return False

def backtrack_solve(sudoku, early_exit = None):
    if (early_exit != None and early_exit.is_set()):
        sys.exit()
    try:
        i = sudoku.index('.')
    except ValueError:
        return True

    for n in range(1,10):
        sudoku[i] = str(n)
        #validate index just performs validation at index i instead of the whole grid
        if (validate_index(sudoku, i) and backtrack_solve(sudoku, early_exit)):
            return True
    sudoku[i] = '.'
    return False

def prune(index, val, poslist):
    indval = val-1
    row = index // 9
    col = index % 9
    box_row = row // 3
    box_col = col // 3
    for i in range(9):
        checkedindex = row*9 + i
        if poslist[checkedindex][indval] == '.':
            poslist[checkedindex][indval] = index
    for j in range(9):
        checkedindex = col + j*9
        if poslist[checkedindex][indval] == '.':
            poslist[checkedindex][indval] = index
    for i in range(3):
        for j in range(3):
            checkedindex = (box_row*3 + i)*9 + (box_col*3 + j)
            if poslist[checkedindex][indval] == '.':
                poslist[checkedindex][indval] = index

def unprune(index, val, poslist):
    indval = val-1
    row = index // 9
    col = index % 9
    box_row = row // 3
    box_col = col // 3
    for i in range(9):
        checkedindex = row*9 + i
        if poslist[checkedindex][indval] == index:
            poslist[checkedindex][indval] = '.'
    for j in range(9):
        checkedindex = col + j*9
        if poslist[checkedindex][indval] == index:
            poslist[checkedindex][indval] = '.'
    for i in range(3):
        for j in range(3):
            checkedindex = (box_row*3 + i)*9 + (box_col*3 + j)
            if poslist[checkedindex][indval] == index:
                poslist[checkedindex][indval] = '.'

#Poslist will keep track of the possible values a square can have without
# immediate violations. The poslist[index][val] is equal to '.' if we can
# put value val into square index without violation, and otherwise is equal
# to the index of the square that would conflict for the first time (that way,
# when we backtrack, we can safely add '.' back a.k.a unprune).
def least_possibilities_solve(sudoku, poslist, early_exit = None):
    if (early_exit != None and early_exit.is_set()):
        sys.exit()
    mincount = 10
    mincountindex = -1
    #Finds the best possible square to perform backtracking.
    for i in range(len(sudoku)):
        if sudoku[i] == '.':
            count = poslist[i].count('.')
            #If count == 0 then there is an empty square that
            # doesn't have any values.
            if (count == 0):
                return False 
            if (mincount > count):
                mincount = count
                mincountindex = i
    #mincountindex == -1 means the grid is full.
    if (mincountindex == -1):
        return True

    for n in range(1,10):
        if (poslist[mincountindex][n-1] == '.'):
            sudoku[mincountindex] = str(n)
            prune(mincountindex,n,poslist)
            if (least_possibilities_solve(sudoku, poslist, early_exit)):
                return True
            unprune(mincountindex,n,poslist)
    sudoku[mincountindex] = '.'
    return False

#Update poslist at the relevant index. change tells us whether or not we are allowed
# to place val at index: if change = 1, then we are allowed, if change=-1, then we are
# not allowed.
def update_poslistcount(index, poslistcount, val, change):
    if (change == 1):
        poslistcount[0][index // 9][val].add(index)
        poslistcount[1][index % 9][val].add(index)
        poslistcount[2][(index // 27)*3 + (index % 9)//3][val].add(index)
    elif (change == -1):
        poslistcount[0][index // 9][val].discard(index)
        poslistcount[1][index % 9][val].discard(index)
        poslistcount[2][(index // 27)*3 + (index % 9)//3][val].discard(index)

def count_prune(index, val, poslist, poslistcount):
    #Previously we didn't need to update poslist for squares
    # with a number filled in, since we never used that information.
    # However, in order to update poslistcount properly, we need
    # to keep track of this information now.
    for i in range(9):
        if poslist[index][i] == '.':
            poslist[index][i] = index
            update_poslistcount(index, poslistcount, i, -1)
    indval = val-1
    row = index // 9
    col = index % 9
    box_row = row // 3
    box_col = col // 3
    for i in range(9):
        checkedindex = row*9 + i
        if poslist[checkedindex][indval] == '.':
            poslist[checkedindex][indval] = index
            update_poslistcount(checkedindex, poslistcount, indval, -1)
    for j in range(9):
        checkedindex = col + j*9
        if poslist[checkedindex][indval] == '.':
            poslist[checkedindex][indval] = index
            update_poslistcount(checkedindex, poslistcount, indval, -1)
    for i in range(3):
        for j in range(3):
            checkedindex = (box_row*3 + i)*9 + (box_col*3 + j)
            if poslist[checkedindex][indval] == '.':
                poslist[checkedindex][indval] = index
                update_poslistcount(checkedindex, poslistcount, indval, -1)

def count_unprune(index, val, poslist, poslistcount):
    for i in range(9):
        if poslist[index][i] == index:
            poslist[index][i] = '.'
            update_poslistcount(index, poslistcount, i, 1)
    indval = val-1
    row = index // 9
    col = index % 9
    box_row = row // 3
    box_col = col // 3
    for i in range(9):
        checkedindex = row*9 + i
        if poslist[checkedindex][indval] == index:
            poslist[checkedindex][indval] = '.'
            update_poslistcount(checkedindex, poslistcount, indval, 1)
    for j in range(9):
        checkedindex = col + j*9
        if poslist[checkedindex][indval] == index:
            poslist[checkedindex][indval] = '.'
            update_poslistcount(checkedindex, poslistcount, indval, 1)
    for i in range(3):
        for j in range(3):
            checkedindex = (box_row*3 + i)*9 + (box_col*3 + j)
            if poslist[checkedindex][indval] == index:
                poslist[checkedindex][indval] = '.'
                update_poslistcount(checkedindex, poslistcount, indval, 1)

#Finds a singleton set in poslistcount, returns the index and associated value
def find_forced(poslistcount):
    for i in range(len(poslistcount)):
        for j in range(len(poslistcount[i])):
            for k in range(len(poslistcount[i][j])):
                if (len(poslistcount[i][j][k]) == 1):
                    for e in poslistcount[i][j][k]:
                        return e, k+1
    return -1, -1

#poslistcount keeps track of the number of square in a row/column/box that
# can have a certain value. When a certain entry is 1, this tells us that
# some row/col/box has only one square in which a value can exist, a.k.a.
# we are forced to put a value in a position
def with_force_solve(sudoku, poslist, poslistcount, early_exit = None):
    if (early_exit != None and early_exit.is_set()):
        sys.exit()
    mincount = 10
    mincountindex = -1
    #Finds the best possible square to evaluate.
    forcedindex, forcedval = find_forced(poslistcount)
    if forcedindex != -1:
        mincountindex = forcedindex
    else:
        for i in range(len(sudoku)):
            if sudoku[i] == '.':
                count = poslist[i].count('.')
                #If count == 0 then there is an empty square that
                # doesn't have any values.
                if (count == 0):
                    return False 
                if (mincount > count):
                    mincount = count
                    mincountindex = i
        #mincountindex == -1 means the grid is full.
        if (mincountindex == -1):
            return True

    for n in range(1,10):
        if (forcedindex == -1 and poslist[mincountindex][n-1] == '.') or forcedval == n:
            sudoku[mincountindex] = str(n)
            count_prune(mincountindex,n,poslist, poslistcount)
            if (with_force_solve(sudoku, poslist, poslistcount, early_exit)):
                return True
            count_unprune(mincountindex,n,poslist, poslistcount)
    sudoku[mincountindex] = '.'
    return False
