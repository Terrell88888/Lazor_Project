import unittest
import time
from lazor import convert_bff, Grid_Structure, Laser_Path, find_fixed_positions, solve_path, solve_lazor
import os


class TestLazor(unittest.TestCase):

    def setUp(self):
        # Use sample configuration file
        self.sample_file = 'mad.bff'
        self.grid, self.num_a_blocks, self.num_b_blocks, self.num_c_blocks, self.laser_start_points, self.target_positions, self.raw_grid = convert_bff(
            self.sample_file)

    def test_convert_bff(self):
        self.assertIsInstance(self.grid, list, "Grid should be a list")
        self.assertGreaterEqual(
            self.num_a_blocks,
            0,
            "A block count should be non-negative")
        self.assertGreaterEqual(
            self.num_b_blocks,
            0,
            "B block count should be non-negative")
        self.assertGreaterEqual(
            self.num_c_blocks,
            0,
            "C block count should be non-negative")
        self.assertIsInstance(
            self.laser_start_points,
            list,
            "Lazor start points should be a list")
        self.assertIsInstance(
            self.target_positions,
            list,
            "Target points should be a list")
        self.assertGreater(len(self.laser_start_points), 0,
                           "There should be at least one lazor start point")
        self.assertGreater(len(self.target_positions), 0,
                           "There should be at least one target point")

    def test_find_fixed_positions(self):
        fixed_positions = find_fixed_positions(self.raw_grid)
        self.assertIsInstance(
            fixed_positions,
            list,
            "Fixed positions should be a list")
        for pos in fixed_positions:
            self.assertEqual(
                len(pos), 2, "Each fixed position should be a 2D coordinate")

    def test_grid_generation(self):
        grid_structure = Grid_Structure(self.grid)
        blocks = ['A'] * self.num_a_blocks + ['B'] * \
            self.num_b_blocks + ['C'] * self.num_c_blocks
        generated_grid = grid_structure.generate_grid(
            blocks, find_fixed_positions(self.raw_grid))

        self.assertEqual(len(generated_grid), len(self.grid),
                         "Generated grid rows should match original grid")
        for row in generated_grid:
            self.assertEqual(
                len(row), len(
                    self.grid[0]), "Generated grid columns should match original grid")

    def test_laser_path_finding(self):
        laser_path = Laser_Path(
            self.grid,
            self.laser_start_points,
            self.target_positions)
        solution = laser_path.calculate_laser_path()

        if solution:
            hit_targets = [point[:2] for path in solution for point in path]
            for target in self.target_positions:
                self.assertIn(
                    target,
                    hit_targets,
                    f"Target point {target} should be hit by lazor")

    def test_solve_path_solution(self):
        expected_block_count = self.num_a_blocks + self.num_b_blocks + self.num_c_blocks
        solution, blocks_used, solved_grid = solve_path(
            self.grid, self.num_a_blocks, self.num_b_blocks, self.num_c_blocks,
            self.laser_start_points, self.target_positions, find_fixed_positions(self.raw_grid)
        )

        self.assertIsNotNone(solution, "A solution should be found")
        self.assertEqual(len([b for b in blocks_used if b in ['A', 'B', 'C']]), expected_block_count,
                         "The number of used blocks should match expected count")

    def test_performance(self):
        start_time = time.time()
        solve_lazor(self.sample_file)
        end_time = time.time()
        self.assertLess(
            end_time - start_time,
            120,
            "Solution should complete within 120 seconds")

    def test_output_image(self):
        output_file = self.sample_file.replace(".bff", "_solved.png")
        solve_lazor(self.sample_file)
        self.assertTrue(
            os.path.exists(output_file),
            "Output image file should be generated")
        os.remove(output_file)  # Clean up after test


if __name__ == '__main__':
    unittest.main()
