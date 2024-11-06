import copy
import time
from PIL import ImageDraw, Image
from sympy.utilities.iterables import multiset_permutations


def convert_bff(file_name):
    """
    Reads a Lazor puzzle configuration file (.bff) and extracts the game board layout, block quantities,
    laser start points, target points, and the original grid structure.
    """
    grid_layout, raw_grid = [], []
    laser_start_points, target_positions = [], []
    num_a_blocks, num_b_blocks, num_c_blocks = 0, 0, 0

    # Read the file and remove whitespace from each line
    with open(file_name, 'r') as f:
        lines = [line.strip() for line in f]

    # Parse each line to extract puzzle elements
    for line in lines:
        if line.startswith('#') or not line:
            continue  # Skip comments and empty lines

        if line == 'GRID START':  # Grid layout start
            grid_layout, raw_grid = parse_grid(
                lines, lines.index('GRID START'))
        elif line.startswith('A'):
            num_a_blocks = extract_block_count(line)  # Reflective block count
        elif line.startswith('B'):
            num_b_blocks = extract_block_count(line)  # Opaque block count
        elif line.startswith('C'):
            num_c_blocks = extract_block_count(line)  # Refractive block count
        elif line.startswith('L'):  # Laser start point
            laser_start_points.append(extract_laser_or_target(line))
        elif line.startswith('P'):  # Target point
            target_positions.append(extract_laser_or_target(line))

    # Expand grid for proper boundary detection and validate configuration
    expanded_grid = expand_grid_with_boundaries(grid_layout)
    validate(
        grid_layout,
        expanded_grid,
        laser_start_points,
        target_positions,
        num_a_blocks,
        num_b_blocks,
        num_c_blocks)
    return expanded_grid, num_a_blocks, num_b_blocks, num_c_blocks, laser_start_points, target_positions, raw_grid


def parse_grid(lines, start_idx):
    """
    Extracts the grid layout between 'GRID START' and 'GRID STOP'.
    """
    grid_layout, raw_grid = [], []
    for line in lines[start_idx + 1:]:
        if line == 'GRID STOP':
            break
        # Remove spaces for cleaner processing
        grid_line = [char for char in line if char != ' ']
        grid_layout.append(grid_line)
        raw_grid.append(grid_line)
    return grid_layout, raw_grid


def extract_block_count(line):
    """
    Extracts the block count (A, B, or C) from the given line.
    """
    digits = ''.join(filter(str.isdigit, line))
    return int(digits) if digits else 0


def extract_laser_or_target(line):
    """
    Extracts laser start point or target point coordinates.
    """
    return [int(coord) for coord in line.split(' ')[1:]]


def expand_grid_with_boundaries(grid_layout):
    """
    Adds boundary markers ('x') around the grid to facilitate laser path validation.
    """
    if not grid_layout:
        raise ValueError("No grid layout found.")

    full_grid = [row[:] for row in grid_layout]
    row_count, col_count = len(full_grid), len(full_grid[0])
    insert_boundary = ['x'] * (2 * col_count + 1)

    # Insert boundaries at appropriate locations in the grid
    for i in range(row_count):
        for j in range(col_count + 1):
            full_grid[i].insert(2 * j, 'x')
    for i in range(row_count + 1):
        full_grid.insert(2 * i, insert_boundary)

    return full_grid


def validate(
        grid_layout,
        expanded_grid,
        laser_start_points,
        target_positions,
        num_reflective,
        num_opaque,
        num_refractive):
    """
    Ensures the configuration meets requirements: checks lasers, blocks, and grid validity.
    """
    rows, cols = len(grid_layout), len(grid_layout[0])

    if not laser_start_points:
        raise ValueError('No laser detected!')
    if (num_reflective + num_opaque + num_refractive) == 0:
        raise ValueError('No blocks available!')
    if (num_reflective + num_opaque + num_refractive) >= rows * cols:
        raise ValueError('Too many blocks!')

    # Validate target and laser points are within boundaries
    for i, target in enumerate(target_positions):
        if not (0 <= target[0] <= cols * 2 and 0 <= target[1] <= rows * 2):
            raise ValueError(f'Target point {i} out of bounds!')

    for i, start_point in enumerate(laser_start_points):
        if not (
                0 <= start_point[0] <= cols *
                2 and 0 <= start_point[1] <= rows *
                2):
            raise ValueError(f'Laser {i} start out of bounds!')
        if not (start_point[2] in [-1, 1] and start_point[3] in [-1, 1]):
            raise ValueError(f'Laser {i} direction invalid!')

    # Check grid characters
    valid_chars = {'x', 'o', 'A', 'B', 'C'}
    for i, row in enumerate(grid_layout):
        for j, char in enumerate(row):
            if char not in valid_chars:
                raise ValueError(f'Invalid character "{char}" at ({j}, {i})!')


class Grid_Structure:
    """
    Represents and manages the Lazor puzzle grid structure.
    """

    def __init__(self, original_grid):
        # Copy original grid structure
        self.original_grid = [row[:] for row in original_grid]
        self.grid_list = None
        self.num_rows = len(original_grid)
        self.num_cols = len(original_grid[0])

    def generate_grid(self, grid_list, fixed_positions):
        """
        Places blocks on the grid according to the list and fixed positions.
        """
        self.grid_list = grid_list[:]
        generated_grid = [row[:] for row in self.original_grid]

        # Place blocks only in available ('o') cells, avoiding fixed positions
        for row in range(self.num_rows):
            for col in range(self.num_cols):
                if [row, col] not in fixed_positions and generated_grid[row][col] == 'o':
                    if self.grid_list:
                        generated_grid[row][col] = self.grid_list.pop(0)

        return generated_grid


class Laser_Path:
    """
    Tracks laser path and handles interactions with blocks in the grid.
    """

    def __init__(self, grid, laser_list, target_list):
        self.grid = grid
        self.laser_list = laser_list
        self.target_list = target_list

    def calculate_laser_path(self):
        """
        Calculates laser paths and checks if all target points are hit.
        """
        result = []
        self.paths = [[laser] for laser in self.laser_list]

        for _ in range(50):
            for path in self.paths:
                if self.update_laser_path(path, result):
                    continue

        return self.paths if len(result) == len(self.target_list) else 0

    def update_laser_path(self, path, result):
        """
        Updates laser path with interactions and checks if targets are hit.
        """
        position, direction = path[-1][:2], path[-1][2:]

        if self.check_position(position, direction):
            return True

        next_step = self.block_interact(position, direction)

        if not next_step:
            path.append([*position, 0, 0])
            if position in self.target_list and position not in result:
                result.append(position)
        elif len(next_step) == 2:
            self.add_path_direction(path, next_step, result)
        elif len(next_step) == 4:
            self.split_path_directions(path, next_step, result)

        return False

    def add_path_direction(self, path, direction, result):
        """
        Adds the next point in the laser's path based on its direction.
        """
        x, y = path[-1][:2]
        new_position = [x + direction[0], y + direction[1]]
        path.append([*new_position, *direction])

        if new_position in self.target_list and new_position not in result:
            result.append(new_position)

    def split_path_directions(self, path, direction, result):
        """
        Splits laser path in two directions if it hits a refractive block.
        """
        x, y = path[-1][:2]
        new_coord1 = [x + direction[0], y + direction[1]]
        new_coord2 = [x, y]

        path.append([*new_coord2, direction[2], direction[3]])
        new_path = [[*new_coord1, direction[0], direction[1]]]
        self.paths.append(new_path)

        if new_coord2 in self.target_list and new_coord2 not in result:
            result.append(new_coord2)

    def block_interact(self, point, direction):
        """
        Determines laser reflection, refraction, or absorption based on block type.
        """
        self.point, self.direction = point, direction

        # Identify block type at the point of interaction
        if point[0] % 2 == 1:
            block_type = self.grid[point[1] + direction[1]][point[0]]
        else:
            block_type = self.grid[point[1]][point[0] + direction[0]]

        return self.block_type_interaction(block_type)

    def block_type_interaction(self, block_type):
        """
        Defines laser behavior based on block type.
        """
        if block_type == 'A':  # Reflective block
            return self.reflect_block()
        elif block_type == 'B':  # Opaque block
            return []
        elif block_type == 'C':  # Refractive block
            return self.refract_block()
        elif block_type in ('o', 'x'):  # Empty or boundary
            return self.direction

    def reflect_block(self):
        """
        Reflects laser in the opposite direction based on grid alignment.
        """
        return [
            self.direction[0] * -1,
            self.direction[1]] if self.point[0] % 2 == 0 else [
            self.direction[0],
            self.direction[1] * -1]

    def refract_block(self):
        """
        Refracts laser in two directions for blocks that allow refraction.
        """
        return [
            self.direction[0],
            self.direction[1],
            self.direction[0] * -1,
            self.direction[1]] if self.point[0] % 2 == 0 else [
            self.direction[0],
            self.direction[1],
            self.direction[0],
            self.direction[1] * -1]

    def check_position(self, laser_coord, direction):
        """
        Checks if laser coordinates exceed grid boundaries.
        """
        width, height = len(self.grid[0]), len(self.grid)
        x, y = laser_coord
        return not (
            0 <= x < width and 0 <= y < height and 0 <= x +
            direction[0] < width and 0 <= y +
            direction[1] < height)


def find_fixed_positions(small_grid):
    positions = []
    for i in range(len(small_grid)):
        for j in range(len(small_grid[0])):
            block = small_grid[i][j]
            if block in ['A', 'B', 'C']:
                positions.append([i * 2 + 1, j * 2 + 1])
    return positions


def is_skip_necessary(grid, possible_positions, holes):
    for i in range(len(holes)):
        x = holes[i][1]
        y = holes[i][0]
        if ((grid[x][y + 1] in ['A', 'B']) and (grid[x][y - 1] in ['A', 'B'])) or \
                ((grid[x + 1][y] in ['A', 'B']) and (grid[x - 1][y] in ['A', 'B'])):
            return False
        else:
            return True


def solve_path(
        grid,
        num_reflective,
        num_opaque,
        num_refractive,
        laser_start_points,
        target_positions,
        fixed_positions):
    blocks = []
    for row in grid:
        for element in row:
            if element == 'o':
                blocks.append(element)
    for i in range(num_reflective):
        blocks[i] = 'A'
    for i in range(num_reflective, num_reflective + num_opaque):
        blocks[i] = 'B'
    for i in range(
            num_reflective +
            num_opaque,
            num_reflective +
            num_opaque +
            num_refractive):
        blocks[i] = 'C'

    block_permutations = list(multiset_permutations(blocks))

    while block_permutations:
        blocks_temp = block_permutations.pop()
        original_grid = Grid_Structure(grid)
        test_board = original_grid.generate_grid(blocks_temp, fixed_positions)

        laser_paths = Laser_Path(
            test_board,
            laser_start_points,
            target_positions)
        solution = laser_paths.calculate_laser_path()

        if solution != 0:
            return solution, blocks_temp, test_board
    return None, None, None


def solve_lazor(file_path):
    grid, num_reflective, num_opaque, num_refractive, lasers, targets, small_grid = convert_bff(
        file_path)
    fixed_positions = find_fixed_positions(small_grid)

    solution, laser_path, solved_grid = solve_path(
        grid, num_reflective, num_opaque, num_refractive, lasers, targets, fixed_positions)

    final_grid = update_grid_with_lasers(small_grid, laser_path)
    output_filename = create_output_image(
        final_grid, solution, lasers, targets, file_path)
    print(f'The puzzle has been solved and saved as {output_filename}')

    return final_grid, solution, laser_path


def update_grid_with_lasers(small_grid, laser_path):
    """
    Updates the grid by placing laser paths in the appropriate cells.
    """
    new_grid = copy.deepcopy(small_grid)
    laser_index = 0
    for row in range(len(new_grid)):
        for col in range(len(new_grid[0])):
            if new_grid[row][col] == 'o':
                new_grid[row][col] = laser_path[laser_index]
                laser_index += 1
    return new_grid


def create_output_image(
        solved_board,
        laser_solution,
        laser_info,
        targets,
        file_path):
    """
    Generates and saves an image of the solved Lazor puzzle.
    """
    output_filename = '.'.join(file_path.split('.')[:-1]) + '_solved.png'
    image_output(
        solved_board=solved_board,
        answer_laser=laser_solution,
        laser_info=laser_info,
        target_points=targets,
        filename=output_filename)
    return output_filename


def solution_color():
    return {
        0: (0, 0, 0),
        'A': (255, 255, 255),
        'B': (0, 0, 0),
        'C': (255, 0, 0),
        'o': (150, 150, 150),
        'x': (100, 100, 100),
    }


def image_output(
        solved_board,
        answer_laser,
        laser_info,
        target_points,
        filename,
        block_size=50):
    """
    Generates and saves an image of the solved Lazor puzzle.
    """
    # Calculate image dimensions
    n_blocks_x, n_blocks_y = len(solved_board[0]), len(solved_board)
    img_width, img_height = n_blocks_x * block_size, n_blocks_y * block_size

    # Initialize the image and color scheme
    colors = solution_color()
    img = Image.new("RGB", (img_width, img_height), color=(0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Draw each block in the grid
    for y in range(n_blocks_y):
        for x in range(n_blocks_x):
            block_color = colors.get(solved_board[y][x], (0, 0, 0))
            top_left = (x * block_size, y * block_size)
            bottom_right = (top_left[0] + block_size, top_left[1] + block_size)
            draw.rectangle([top_left, bottom_right], fill=block_color)

    # Draw grid lines
    draw_grid_lines(draw, img_width, img_height, block_size,
                    colors.get(0, (200, 200, 200)))

    draw_laser_paths(draw, answer_laser, laser_info, block_size)

    draw_target_points(draw, target_points, block_size)

    output_filename = filename if filename.endswith(
        ".png") else f"{filename.split('.')[0]}_solved.png"
    img.save(output_filename)
    print(f'Solved puzzle image saved as {output_filename}')


def draw_grid_lines(draw, img_width, img_height, block_size, line_color):
    for y in range(0, img_height, block_size):
        draw.line([(0, y), (img_width, y)], fill=line_color, width=2)
    for x in range(0, img_width, block_size):
        draw.line([(x, 0), (x, img_height)], fill=line_color, width=2)


def draw_laser_paths(draw, answer_laser, laser_info, block_size):
    for laser in laser_info:
        x, y = laser[0] * block_size / 2, laser[1] * block_size / 2
        draw.ellipse([x - 5, y - 5, x + 5, y + 5], fill=(255, 0, 0))

    for path in answer_laser:
        for i in range(len(path) - 1):
            start = (path[i][0] * block_size / 2, path[i][1] * block_size / 2)
            end = (path[i + 1][0] * block_size / 2,
                   path[i + 1][1] * block_size / 2)
            draw.line([start, end], fill=(255, 0, 0), width=2)


def draw_target_points(draw, target_points, block_size):
    for target in target_points:
        x, y = target[0] * block_size / 2, target[1] * block_size / 2
        draw.ellipse([x - 5, y - 5, x + 5, y + 5],
                     fill=(255, 255, 255), outline="red", width=2)


def main():
    """
    Solves multiple Lazor puzzles and reports time taken for each.
    """
    bff_files = [
        'D:\\Lazor_project\\bff_files\\dark_1.bff',
        'D:\\Lazor_project\\bff_files\\mad_1.bff',
        'D:\\Lazor_project\\bff_files\\mad_4.bff',
        'D:\\Lazor_project\\bff_files\\mad_7.bff',
        'D:\\Lazor_project\\bff_files\\numbered_6.bff',
        'D:\\Lazor_project\\bff_files\\showstopper_4.bff',
        'D:\\Lazor_project\\bff_files\\tiny_5.bff',
        'D:\\Lazor_project\\bff_files\\yarn_5.bff'
    ]

    total_start_time = time.time()
    for bff_file in bff_files:
        start_time = time.time()
        solve_lazor(bff_file)
        end_time = time.time()
        print(f'{bff_file} solved in {end_time - start_time:.2f} seconds')

    total_end_time = time.time()
    print(f'Total time taken: {total_end_time - total_start_time:.2f} seconds')


if __name__ == "__main__":
    main()