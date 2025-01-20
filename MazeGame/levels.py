import numpy as np
import random
from collections import deque

DIRECTIONS = [(0, 1), (1, 0), (0, -1), (-1, 0)]

def generate_maze(level, width, height, grid_size):
    level = min(50, max(1, level))

    maze_width, maze_height = get_maze_size(level, width, height, grid_size)
    maze = initialize_maze(maze_width, maze_height)
    create_paths(maze, maze_width, maze_height)

    if level > 2:
        add_complexity(maze, level)

    ensure_exit_reachable(maze, maze_width, maze_height)
    min_moves = calculate_min_moves(maze)
    if min_moves == float('inf'):
        connect_start_and_exit(maze, maze_width, maze_height)
        min_moves = calculate_min_moves(maze)
    return maze, max(min_moves - 1, 0)

def get_maze_size(level, width, height, grid_size):
    max_cells_width = width // grid_size
    max_cells_height = height // grid_size

    base_size = 15 + (level // 2)  # زيادة الحجم الأساسي للمتاهة
    size_increment = level  # زيادة حجم المتاهة بشكل أكبر مع زيادة المستوى
    maze_width = min(base_size + size_increment, max_cells_width)
    maze_height = min(base_size + size_increment, max_cells_height)

    return maze_width, maze_height

def add_complexity(maze, level):
    height, width = maze.shape
    num_extra_walls = level * 2  # زيادة عدد الجدران الإضافية

    for _ in range(num_extra_walls):
        x = random.randint(2, width - 2)
        y = random.randint(2, height - 2)

        temp_maze = maze.copy()
        temp_maze[y][x] = 1

        if calculate_min_moves(temp_maze) != float('inf'):
            maze[y][x] = 1

        if level > 20 and random.random() < 0.5:  # زيادة احتمالية إضافة جدران إضافية
            x1, y1 = random.randint(1, width - 2), random.randint(1, height - 2)
            maze[y1][x1] = 1  # إضافة جدار إضافي

def initialize_maze(maze_width, maze_height):
    maze = np.ones((maze_height, maze_width), dtype=int)
    maze[0][0] = 0
    return maze

def create_paths(maze, maze_width, maze_height):
    stack = [(0, 0)]
    while stack:
        x, y = stack[-1]
        neighbors = find_neighbors(maze, x, y, maze_width, maze_height)
        if neighbors:
            nx, ny, dx, dy = random.choice(neighbors)
            maze[ny][nx] = 0
            maze[y + dy][x + dx] = 0
            stack.append((nx, ny))
        else:
            stack.pop()
    # تقليل عدد المسارات المفتوحة
    for y in range(1, maze_height - 1):
        for x in range(1, maze_width - 1):
            if maze[y][x] == 0 and random.random() < 0.3:  # إغلاق بعض المسارات بشكل عشوائي
                maze[y][x] = 1

def ensure_exit_reachable(maze, maze_width, maze_height):
    if maze[maze_height - 2][maze_width - 1] == 1 and maze[maze_height - 1][maze_width - 2] == 1:
        maze[maze_height - 1][maze_width - 2] = 0
    maze[maze_height - 1][maze_width - 1] = 0

def find_neighbors(maze, x, y, maze_width, maze_height):
    neighbors = []
    for dx, dy in DIRECTIONS:
        nx, ny = x + dx * 2, y + dy * 2
        if is_valid_cell(maze, nx, ny, maze_width, maze_height):
            neighbors.append((nx, ny, dx, dy))
    return neighbors

def is_valid_cell(maze, x, y, maze_width, maze_height):
    if 0 <= x < maze_width and 0 <= y < maze_height and maze[y][x] == 1:
        wall_count = 0
        for dx, dy in DIRECTIONS:
            nx, ny = x + dx, y + dy
            if 0 <= nx < maze_width and 0 <= ny < maze_height and maze[ny][nx] == 1:
                wall_count += 1
        return wall_count >= 3
    return False

def calculate_min_moves(maze):
    maze_height, maze_width = maze.shape
    start = (0, 0)
    goal = (maze_height - 1, maze_width - 1)
    queue = deque([start])
    distances = {start: 0}

    while queue:
        x, y = queue.popleft()
        if (x, y) == goal:
            return distances[(x, y)]
        for dx, dy in DIRECTIONS:
            nx, ny = x + dx, y + dy
            if 0 <= nx < maze_width and 0 <= ny < maze_height and maze[ny][nx] == 0:
                if (nx, ny) not in distances:
                    queue.append((nx, ny))
                    distances[(nx, ny)] = distances[(x, y)] + 1
    return float('inf')

def connect_start_and_exit(maze, maze_width, maze_height):
    start = (0, 0)
    goal = (maze_height - 1, maze_width - 1)
    queue = deque([start])
    parent = {start: None}

    while queue:
        x, y = queue.popleft()
        if (x, y) == goal:
            while (x, y) != start:
                maze[y][x] = 0
                x, y = parent[(x, y)]
            maze[start[1]][start[0]] = 0
            return
        for dx, dy in DIRECTIONS:
            nx, ny = x + dx, y + dy
            if 0 <= nx < maze_width and 0 <= ny < maze_height and maze[ny][nx] == 0 and (nx, ny) not in parent:
                parent[(nx, ny)] = (x, y)
                queue.append((nx, ny))

if __name__ == "__main__":
    width, height, grid_size = 800, 600, 40
    level = 50
    maze, min_moves = generate_maze(level, width, height, grid_size)
    for row in maze:
        print("".join([' ' if cell == 0 else '#' for cell in row]))
    print(f"Minimum moves: {min_moves}")
