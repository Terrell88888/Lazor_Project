# Lazor_Project

This project, part of EN 540.635 Software Carpentry, focuses on using Python to automatically solve the Lazor game available on iOS and Android. The objective is to generate both a visual solution and a text file output for each solution.

## Overview
The Lazor puzzle solver reads configurations from .bff files and simulates the paths of lasers as they interact with different block types. It then identifies valid solutions that ensure all target points are hit. Each solution is output an image (.png), making it straightforward to visualize and verify.

## How to Use
1. Download main.py and ensure all .bff files are in the same folder..
2. Choose the puzzle you want to solve and run lazor.py to enter the file name of the puzzle.
3. The program will generate a .png image showing the solution and print solution details to the console.

## Code Structure

### **1. Core Classes**
  - **Grid_Structure**: Manages the Lazor puzzle grid layout.
  
  - **Laser_Path**: Handles the movement of the laser in the grid and interaction with different block types.

### **2. Main functions**

  - **convert_bff(file_name):** Reads `.bff` puzzle configuration file and extracts key components such as grid layout, number of blocks, laser start and target points.
  
  - **parse_grid(lines, start_idx):** Parses the grid layout between "GRID START" and "GRID STOP" markers.
  
  - **validate() and auxiliary functions:**
  - `validate()`: Validates the overall puzzle configuration.
  - Auxiliary functions (`extract_block_count`, `expand_grid_with_boundaries`, etc.) support parsing and preparing puzzles for solving.

### **3. Helper Functions**

  - **find_fixed_positions():** Finds the positions of fixed blocks in the mesh.
  - **solve_path()** and **solve_lazor()**: Core functions that coordinate the puzzle solving process, generate block configurations, check solutions, and create output meshes.

### **4. Image Generation Functions**

  - **create_output_image()**: Generates an image of the solved puzzle, including laser paths and target points.

   - **image_output()** Handles visualization of the grid, laser path, and target.



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

## Unit Testing

Tests such as file parsing, mesh generation, path calculation, performance evaluation and output validation ensured the correctness and reliability of the project's main functions.

### 1. `test_convert_bff`:Verify the correctness of `convert_bff` function.
  - **Test content**:
  - Ensure that `grid` is a list and contains grid information.
  - Confirm that the number of blocks of type A, B, and C are all non-negative.
  - Verify that the type of laser start point and target point is a list, and ensure that there is at least one laser start point and one target point.

### 2. `test_find_fixed_positions`:Check that the `find_fixed_positions` function finds the fixed block positions correctly.
  - **Test content**.
  - Ensure that `find_fixed_positions` returns a list type.
  - Verify that each fixed position is a 2D coordinate, making sure it is formatted correctly.

### 3. `test_grid_generation`:Verify the ability of the `Grid_Structure` class to generate a grid.
  - **Test content**:
  - Generate a new grid using the given A, B, C blocks.
  - Make sure the generated grid has the same number of rows and columns as the original grid, verifying the consistency of the grid size.

### 4. `test_laser_path_finding`:Tests the laser path calculation functionality of the `Laser_Path` class.
  - **Test content**.
  - Call the `calculate_laser_path` method to calculate the laser path.
  - Verify that all target points are hit by the laser, making sure that the path contains all target points.

### 5. `test_solve_path_solution`:Check the solving ability of the `solve_path` function.
  - **Test content**:
  - Ensure that the function can find a valid solution.
  - Verify that the number of blocks used is equal to the expected number of blocks, ensuring that the solution has the required number of blocks.

### 6. `test_performance`:Test the performance of the overall solution process.
  - **Test content**.
  - Solve the problem using the `solve_lazor` method and calculate the completion time.
  - Verify that the solving time is less than 120 seconds to ensure that the algorithm completes in a reasonable amount of time.

### 7. `test_output_image`:Function to generate output images after checking the solution.
  - **Test content**.
  - Call the `solve_lazor` method to solve the problem and check if the appropriate output image file is generated.
  - Verify that the image file exists and delete it after the test to clean up the environment.


## Contributors
- Gangxiang Tang: gtang11@jh.edu
- Guanbo Wang: gwang66@jh.edu
