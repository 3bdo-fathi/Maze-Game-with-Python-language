import numpy as np  # Math library to be used for maze generation
import random  # To generate random maze
from collections import deque  # To calculate distances

# Directions
DIRECTIONS = [(0, 1), (1, 0), (0, -1), (-1, 0)]


# Maze generation function - creates a new maze at each level
def generate_maze(level, width, height, grid_size):
    # Calculate the maze size based on the level
    maze_width, maze_height = get_maze_size(level, width, height, grid_size)

    # Initialize an empty maze with walls
    maze = initialize_maze(maze_width, maze_height)

    # Create random paths
    create_paths(maze, maze_width, maze_height)

    # Ensure the exit is reachable
    ensure_exit_reachable(maze, maze_width, maze_height)

    # Calculate the minimum number of steps to reach the exit
    min_moves = calculate_min_moves(maze)

    # If no solution, connect start to exit
    if min_moves == float('inf'):
        connect_start_and_exit(maze, maze_width, maze_height)
        min_moves = calculate_min_moves(maze)

    # Return the maze and the minimum moves
    return maze, max(min_moves - 1, 0)


# Function to calculate the maze size - the higher the level, the harder the maze
def get_maze_size(level, width, height, grid_size):
    # Calculate the maximum possible space on the screen
    max_cells_width = width // grid_size
    max_cells_height = height // grid_size

    # Base size and increment based on the level
    base_size = 5
    size_increment = level // 2

    # Determine the maze size while respecting the maximum limit
    maze_width = min(base_size + size_increment, max_cells_width)
    maze_height = min(base_size + size_increment, max_cells_height)

    return maze_width, maze_height


# Maze initialization function - sets all cells as walls
def initialize_maze(maze_width, maze_height):
    # Create an array filled with ones (walls)
    maze = np.ones((maze_height, maze_width), dtype=int)

    # Open the starting point
    maze[0][0] = 0
    return maze


# Path creation function - random algorithm to open paths
def create_paths(maze, maze_width, maze_height):
    # Start from the initial point
    stack = [(0, 0)]

    # Continue until all paths are created
    while stack:
        x, y = stack[-1]

        # Find possible neighbors
        neighbors = find_neighbors(maze, x, y, maze_width, maze_height)

        # If there are neighbors, choose a random one and open the path
        if neighbors:
            nx, ny, dx, dy = random.choice(neighbors)
            maze[ny][nx] = 0
            maze[y + dy][x + dx] = 0
            stack.append((nx, ny))

        # If no neighbors, backtrack to the previous cell
        else:
            stack.pop()


# Function to ensure the exit is reachable
def ensure_exit_reachable(maze, maze_width, maze_height):
    # If the exit is blocked, open it
    if maze[maze_height - 2][maze_width - 1] == 1 and maze[maze_height - 1][maze_width - 2] == 1:
        maze[maze_height - 1][maze_width - 2] = 0

    # Make sure the exit is open
    maze[maze_height - 1][maze_width - 1] = 0


# Function to find valid neighboring cells
def find_neighbors(maze, x, y, maze_width, maze_height):
    neighbors = []

    # Check neighbors in all directions
    for dx, dy in DIRECTIONS:
        nx, ny = x + dx * 2, y + dy * 2

        # Ensure the neighbor is valid
        if is_valid_cell(maze, nx, ny, maze_width, maze_height):
            neighbors.append((nx, ny, dx, dy))
    return neighbors


# Function to check if a cell is valid
def is_valid_cell(maze, x, y, maze_width, maze_height):
    # Ensure the cell is within bounds and is a wall
    if 0 <= x < maze_width and 0 <= y < maze_height and maze[y][x] == 1:
        wall_count = 0

        # Count the number of walls around the cell
        for dx, dy in DIRECTIONS:
            nx, ny = x + dx, y + dy
            if 0 <= nx < maze_width and 0 <= ny < maze_height and maze[ny][nx] == 1:
                wall_count += 1

        # Ensure the cell is surrounded by walls
        return wall_count >= 3
    return False


# Function to calculate the minimum number of steps to reach the exit
def calculate_min_moves(maze):
    maze_height, maze_width = maze.shape
    start = (0, 0)
    goal = (maze_height - 1, maze_width - 1)

    # Use breadth-first search to calculate shortest path
    queue = deque([start])
    distances = {start: 0}

    while queue:
        x, y = queue.popleft()

        # If we've reached the exit, return the number of steps
        if (x, y) == goal:
            return distances[(x, y)]

        # Move in all directions
        for dx, dy in DIRECTIONS:
            nx, ny = x + dx, y + dy

            # Ensure the move is valid
            if 0 <= nx < maze_width and 0 <= ny < maze_height and maze[ny][nx] == 0:
                if (nx, ny) not in distances:
                    queue.append((nx, ny))
                    distances[(nx, ny)] = distances[(x, y)] + 1

    # If no path exists, return infinity
    return float('inf')


# Function to connect the start point to the exit
def connect_start_and_exit(maze, maze_width, maze_height):
    x, y = 0, 0

    # Move from start to exit
    while (x, y) != (maze_height - 1, maze_width - 1):
        if x < maze_width - 1:
            x += 1
        elif y < maze_height - 1:
            y += 1

        # Open the path
        maze[y][x] = 0


# Main code - running the file standalone
if __name__ == "__main__":
    # Basic settings
    width, height, grid_size = 800, 600, 40
    level = 1

    # Generate the maze
    maze, min_moves = generate_maze(level, width, height, grid_size)

    # Print the maze
    for row in maze:
        print("".join([' ' if cell == 0 else '#' for cell in row]))

    # Print the minimum number of steps
    print(f"Minimum moves: {min_moves}")
