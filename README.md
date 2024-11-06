# Lazor_Project

This project, part of EN 540.635 Software Carpentry, focuses on using Python to automatically solve the Lazor game available on iOS and Android. The objective is to generate both a visual solution and a text file output for each solution.

## Overview
The Lazor puzzle solver reads configurations from .bff files and simulates the paths of lasers as they interact with different block types. It then identifies valid solutions that ensure all target points are hit. Each solution is output an image (.png), making it straightforward to visualize and verify.

## How to Use
1. Download main.py and ensure all .bff files are in the same folder..
2. Choose the puzzle you want to solve and run main.py to enter the file name of the puzzle.
3. The program will generate a .png image showing the solution and print solution details to the console.

## Code Structure

- `main.py`: Main script for solving puzzles.
- `bff_convertor()`: Parses `.bff` files and extracts game configurations.
- `Grid_part` **Class**: Manages the grid structure and block placements.
- `Lazor_part` **Class**: Handles laser path calculations and interactions.
- `image_output()`: Generates and saves a visual output of the solution.
- 
### Example:

```plaintext
# This is a comment
# This example is for mad 1 in Lazor
#   x = no block allowed
#   o = blocks allowed
#   A = fixed reflect block
#   B = fixed opaque block
#   C = fixed refract block

# Grid will start at top left being 0, 0
# Step size is by half blocks
# Thus, this leads to even numbers indicating
# the rows/columns between blocks, and odd numbers
# intersecting blocks.

GRID START
o   o   o   o
o   o   o   o
o   o   o   o
o   o   o   o
GRID STOP

# Here we specify that we have 5 reflect blocks
A 2
C 1

# Now we specify that we have two lazers
#    x, y, vx, vy
# NOTE! because 0, 0 is the top left, our axis
# are as follows:
#
#      __________\ +x
#      |         /
#      |
#      |
#      |
#     \|/ +y
#      
L 2 7 1 -1

# Here we have the points that we need the lazers to intersect
P 3 0
P 4 3
P 2 5
P 4 7
```

## Output

The solution will generate:

- A `.png` image visualizing the board with laser paths.
- Console output indicating the time taken and solution details.
![214bfb4852070f30722f739ad9a8a82](https://github.com/user-attachments/assets/342c26b6-e731-497e-b114-476f81a6bcd4)



## Contributors
- Gangxiang Tang
- Guanbo Wang: gwang66@jh.edu, gwang66
