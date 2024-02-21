# Lucky's Sudoku Solver

This repo contains several algorithms to solve sudokus. The code was originally made for [an article on Lucky's Corner](https://www.luckys-corner.com/2024/2/sudoku/).

# Dependencies

The UI element requires [PyGame](https://www.pygame.org/docs/) to run.

Furthermore, this project doesn't come with sudoku puzzles. You will have to aquire them yourselves.

# Usage

To use the UI element, simply run

```bash
python ui.py
```

Once the program start running, you can use the buttons to control the program. Once you've loaded in a puzzle, you can also enter numbers into the square by first clicking on a square, or press BACKSPACE to remove a number.

# Sudoku Files

For this project, I used files from [t-dillon](https://github.com/t-dillon/tdoku/blob/master/data.zip). You are, of course, free to use any file you find. The files need to be in the following format:

- Each line in the file represents one sudoku,
- A sudoku should be stored in 'reading order'; the digits of a sudoku grid should be written from left to right, then top to bottom,
- Any symbol, or indeed a collection of symbols, can be used to represent an empty space,
- No symbol can or should be used to represent the end of a row/block,
- Any line that starts with # will be ignored.

Furthermore, any file that starts with a period (i.e. .sudoku_file) will be ignored by the program.
<<<<<<< HEAD

Simply place the files into the sudoku_grids folder, and the program should detect them.
=======
>>>>>>> 75155d6922354207f851527d215a05f3a59cfff9
