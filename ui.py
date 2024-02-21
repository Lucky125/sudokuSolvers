import sys, pygame, os, random, threading, time
from sudoku_solver import is_valid_with_errors, solve, SOLVE_METHODS

SUDOKUS_DIRECTORY = 'sudoku_grids\\'

def get_random_sudoku_grid():
    files = [f for f in os.listdir(SUDOKUS_DIRECTORY) if f[0] != '.']
    if (len(files) == 0):
        return None
    filename = random.choice(files)
    file = open(SUDOKUS_DIRECTORY + filename, 'r')
    linenum = 0
    for _ in file:
        linenum += 1
    sudoku = None
    attempt = 0
    while (sudoku == None and attempt < 100):
        attempt += 1
        chosenline = random.randint(0,linenum-1)
        file.seek(0)
        for _ in range(chosenline):
            file.readline() 
        sudoku = file.readline()
        if (sudoku[0] == '#'):
            sudoku = None
    file.close()
    return sudoku

def get_all_sudokus():
    files = [f for f in os.listdir(SUDOKUS_DIRECTORY) if f[0] != '.']
    sudokus = []
    for filename in files:
        with open(SUDOKUS_DIRECTORY + filename, 'r') as file:
            sudokus += file.read().split('\n')
    return [s for s in sudokus if len(s) >= 81 and (s[0] != '#')]

def str_to_grid(str):
    grid = ['.']*81
    for i in range(min(len(str),81)):
        if (str[i] in '123456789'):
            grid[i] = str[i]
    return grid 


#----------------- VISUALS -----------------

pygame.init()

grid = [] 
active_cell = None

PASSIVE = 0
ERROR = 1
ALL_GREEN = 2
grid_display_mode = PASSIVE

APP_MARGIN = 100, 100
GRID_CELL_SIZE = 50
GRID_MARGIN = 5
BLOCK_MARGIN = 5
OPTION_WIDTH = 500
OPTION_HEIGHT = 100
OPTIONS_MARGIN = 10
OPTION_GRID_MARGIN = 50
LINE_HEIGHT = 40
LINE_MARGIN = 5
LINE_NUM = 5
LINE_GRID_MARGIN = 40
WHITE = pygame.Color(255,255,255)
GREY = pygame.Color(127,127,127)
BLACK = pygame.Color(0,0,0)
YELLOW = pygame.Color(255,255,0)
RED = pygame.Color(255,127,127)
GREEN = pygame.Color(127, 255, 127)
FONT = pygame.font.Font(None, 64)
SMALL_FONT = pygame.font.Font(None, 32)

width = APP_MARGIN[0]*2 + GRID_CELL_SIZE*9 + GRID_MARGIN*8 + BLOCK_MARGIN*2 + OPTION_WIDTH + OPTION_GRID_MARGIN
height = APP_MARGIN[1]*2 + GRID_CELL_SIZE*9 + GRID_MARGIN*8 + BLOCK_MARGIN*2 + LINE_GRID_MARGIN + LINE_NUM*LINE_HEIGHT + (LINE_NUM-1)*LINE_MARGIN
size = width, height
screen = pygame.display.set_mode(size)

solve_method = 0

options_grid = []
lines = ['']*LINE_NUM

class Cell():
    def __init__(self, left, top):
        self.left = left
        self.top = top
        self.rect = pygame.Rect(left, top, GRID_CELL_SIZE, GRID_CELL_SIZE)
        self.val = None
        self.editable = False
        self.warning = False

    def collidepoint(self, point):
        return self.rect.collidepoint(point)

class Option():
    def __init__(self, left, top, text, command):
        self.left = left
        self.top = top
        self.rect = pygame.Rect(left, top, OPTION_WIDTH, OPTION_HEIGHT)
        self.text = text
        self.command = command

    def collidepoint(self, point):
        return self.rect.collidepoint(point)

    def execute(self):
        self.command()

def render_cell(cell):
    if (cell == active_cell):
        pygame.draw.rect(screen, YELLOW, cell.rect)
    elif (grid_display_mode == ALL_GREEN):
        pygame.draw.rect(screen, GREEN, cell.rect)
    elif (grid_display_mode == ERROR and cell.warning):
        pygame.draw.rect(screen, RED, cell.rect)
    else:
        pygame.draw.rect(screen, WHITE, cell.rect)
    if (cell.val != None):
        if (cell.editable):
            text = FONT.render(cell.val, True, BLACK)
        else:
            text = FONT.render(cell.val, True, GREY)
        text_rect = text.get_rect(centerx=cell.left + GRID_CELL_SIZE/2, centery=cell.top + GRID_CELL_SIZE/2)
        screen.blit(text, text_rect)

def render_option(option):
    pygame.draw.rect(screen, WHITE, option.rect)
    text = FONT.render(option.text, True, BLACK)
    text_rect = text.get_rect(centerx=option.left + OPTION_WIDTH/2, centery=option.top + OPTION_HEIGHT/2)
    screen.blit(text, text_rect)

def render_lines():
    for i in range(LINE_NUM):
        if (len(lines) == i):
            return 
        text = SMALL_FONT.render(lines[i], True, BLACK)
        text_rect = text.get_rect(x=APP_MARGIN[0], centery=APP_MARGIN[1]+GRID_CELL_SIZE*9+GRID_MARGIN*8+LINE_GRID_MARGIN+LINE_HEIGHT/2 + (LINE_HEIGHT+LINE_MARGIN)*i)
        screen.blit(text, text_rect)

def render_solve_method():
    solve_method_text = "Using {0}".format(SOLVE_METHODS[solve_method][1])
    text = SMALL_FONT.render(solve_method_text, True, BLACK)
    text_rect = text.get_rect(x=APP_MARGIN[0], centery=(0.75)*APP_MARGIN[1])
    screen.blit(text, text_rect)

def render_all():
    screen.fill(GREY)
    for c in grid:
        render_cell(c)

    for o in options_grid:
        render_option(o)

    render_lines()
    render_solve_method()
    pygame.display.flip()

def create_grid():
    global grid
    grid = []
    for i in range(9):
        for j in range(9):
            grid.append(Cell(APP_MARGIN[0]+(GRID_CELL_SIZE + GRID_MARGIN)*j + BLOCK_MARGIN*(j//3),
                             APP_MARGIN[1]+(GRID_CELL_SIZE + GRID_MARGIN)*i + BLOCK_MARGIN*(i//3)))

def create_options():
    global options_grid
    options_grid = []
    for i in range(len(options)):
        options_grid.append(Option(APP_MARGIN[0]+GRID_CELL_SIZE*9+GRID_MARGIN*8+BLOCK_MARGIN*2+OPTION_GRID_MARGIN, APP_MARGIN[1] + (OPTION_HEIGHT + OPTIONS_MARGIN)*i, options[i][0], options[i][1]))

def set_grid_vals(vals):
    i = 0
    while (i < min(len(vals), len(grid))):
        if (vals[i] in '123456789'):
            grid[i].val = vals[i]
            grid[i].editable = False
        else:
            grid[i].val = None
            grid[i].editable = True
        i += 1

def fill_grid_vals(vals):
    i = 0
    while (i < min(len(vals), len(grid))):
        if (vals[i] in '123456789'):
            grid[i].val = vals[i]
        else:
            grid[i].val = None
        i += 1

def extract_vals():
    vals = []
    for cell in grid:
        if (cell.val != None):
            vals.append(cell.val)
        else:
            vals.append('.')
    return vals

def check_grid_if_valid():
    global grid_display_mode
    errors = is_valid_with_errors(extract_vals())
    if (len(errors) == 0):
        grid_display_mode = ALL_GREEN
        return
    grid_display_mode = ERROR
    for i in range(len(grid)):
        if ('row',i//9) in errors or ('col', i % 9) in errors or ('box', i // 27, (i // 3) % 3) in errors:
            grid[i].warning = True
        else:
            grid[i].warning = False

def load_random_puzzle():
    global lines
    global grid_display_mode
    grid_display_mode = PASSIVE
    random_sudoku = get_random_sudoku_grid()
    if (random_sudoku == None):
       lines = ['Error, sudoku file not found.','Please ensure there are valid files in the sudoku_grid directory.']
    set_grid_vals(random_sudoku)

def solve_current_puzzle_thread(vals, solve_method, result, early_exit):
    result[0] = solve(vals, solve_method, early_exit)

def solve_current_puzzle():
    global lines
    global grid_display_mode
    grid_display_mode = PASSIVE
    lines = ['Press Escape to abort']
    vals = extract_vals()
    result = [None]
    early_exit = threading.Event()
    solver = threading.Thread(target=solve_current_puzzle_thread, args=(vals,SOLVE_METHODS[solve_method][0], result, early_exit))
    solver.start()
    while(solver.is_alive()):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                early_exit.set()
                solver.join()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if (event.key == pygame.K_ESCAPE):
                    early_exit.set()
                    solver.join()
        copy_vals = vals.copy()
        fill_grid_vals(copy_vals)
        render_all()
        time.sleep(0.1)
    if (not result[0]):
        lines = ["Error, could not solve sudoku."]
    else:
        lines = ['']
    fill_grid_vals(vals)

def change_solve_method():
    global solve_method
    solve_method = (solve_method + 1)% len(SOLVE_METHODS)

def solve_all_thread(puzzles, total, solve_method, early_exit):
    for p in puzzles:
        if (early_exit.is_set()):
            return
        solve(p, solve_method, early_exit)
        total[0] += 1

def solve_all():
    global lines
    lines = ['Preparing test, application may freeze temporarily']
    render_all()
    total = [0]
    puzzles = [str_to_grid(p) for p in get_all_sudokus()]
    totalpuzzles = len(puzzles)
    early_exit = threading.Event()
    solver = threading.Thread(target=solve_all_thread, args=(puzzles,total,SOLVE_METHODS[solve_method][0], early_exit))
    start_time = time.time()
    solver.start()
    while(solver.is_alive()):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                early_exit.set()
                solver.join()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if (event.key == pygame.K_ESCAPE):
                    early_exit.set()
                    solver.join()
        current_time = int(time.time()-start_time)
        lines = ['Solved {total:d} of {totalpuzzles:d} sudokus.'.format(total=total[0], totalpuzzles=totalpuzzles), 'Time Elapsed: {minute:d}:{second:02d}.'.format(minute=current_time // 60, second=current_time % 60), 'Press Escape to abort.']
        render_all()
        time.sleep(0.3)
    total_time = int(time.time()-start_time)
    lines = ['Completed {total:d} of {totalpuzzles:d} sudokus.'.format(total=total[0], totalpuzzles=totalpuzzles), 'Total Time: {minute:d}:{second:02d}'.format(minute=total_time//60,second=total_time % 60)]

def clear_board():
    global grid_display_mode
    grid_display_mode = PASSIVE
    for c in grid:
        if (c.editable):
            c.val = None

options = [
    ('Check if grid is valid', check_grid_if_valid),
    ('Load new puzzle', load_random_puzzle),
    ('Solve', solve_current_puzzle),
    ('Change solve method', change_solve_method),
    ('Solve all sudokus', solve_all),
    ('Clear Board', clear_board),
]

create_grid()
create_options()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT: sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            for o in options_grid:
                if (o.collidepoint(event.pos)):
                    o.execute()
            active_cell = None
            for c in grid:
                if (c.editable and c.collidepoint(event.pos)):
                    active_cell = c 
        elif event.type == pygame.KEYDOWN:
            if (active_cell != None):
                if (pygame.key.name(event.key) in '123456789'):
                    active_cell.val = pygame.key.name(event.key)
                    active_cell = None
                    grid_display_mode = PASSIVE
                elif (event.key == pygame.K_BACKSPACE):
                    active_cell.val = None
                    active_cell = None 
                    grid_display_mode = PASSIVE

   
    render_all()
