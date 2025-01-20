import pygame
import sys
import random
from collections import deque
import numpy as np
from levels import generate_maze

pygame.init()
pygame.display.set_caption("Maze Game")

screen_info = pygame.display.Info()
WIDTH = screen_info.current_w
HEIGHT = screen_info.current_h
PADDING = max(20, int(min(WIDTH, HEIGHT) * 0.05))
FPS = 90 if max(WIDTH, HEIGHT) >= 1200 else 60

screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
clock = pygame.time.Clock()

def resize_screen():
    global WIDTH, HEIGHT, PADDING, FPS
    WIDTH, HEIGHT = pygame.display.get_surface().get_size()
    PADDING = max(20, int(min(WIDTH, HEIGHT) * 0.05))
    FPS = 90 if max(WIDTH, HEIGHT) >= 1200 else 60

COLORS = {
    'background': (18, 18, 32),
    'wall': (45, 45, 60),
    'path': (220, 225, 235),
    'player': (255, 87, 34),
    'exit': (76, 175, 80),
    'text': (235, 235, 245),
    'visited': (115, 165, 210),
    'button': (55, 71, 79),
    'button_hover': (77, 96, 107),
    'menu_bg': (28, 28, 48),
    'back_button': (183, 28, 28),
    'back_button_hover': (211, 47, 47)
}

main_font = pygame.font.Font(None, 80)
game_font = pygame.font.Font(None, 40)
small_font = pygame.font.Font(None, 30)

class Button:
    def __init__(self, x, y, width, height, text, font=game_font, color=COLORS['button'],
                 hover_color=COLORS['button_hover']):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.is_hovered = False
        self.color = color
        self.hover_color = hover_color

    def draw(self, surface):
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(surface, color, self.rect, border_radius=10)
        pygame.draw.rect(surface, COLORS['text'], self.rect, 2, border_radius=10)
        text_surface = self.font.render(self.text, True, COLORS['text'])
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.is_hovered:
                return True
        return False

class BackButton(Button):
    def __init__(self, x, y):
        super().__init__(x, y, 100, 40, "Back", small_font,
                        COLORS['back_button'], COLORS['back_button_hover'])

def create_particle_effect(x, y, color, size):
    particles = []
    for _ in range(15):
        angle = random.uniform(0, 2 * np.pi)
        speed = random.uniform(2, 5)
        dx = np.cos(angle) * speed
        dy = np.sin(angle) * speed
        lifetime = random.uniform(20, 40)
        particles.append({
            'x': x, 'y': y,
            'dx': dx, 'dy': dy,
            'size': random.randint(2, size // 2),
            'lifetime': lifetime,
            'max_lifetime': lifetime,
            'color': color
        })
    return particles

def update_particles(particles):
    alive_particles = []
    for p in particles:
        p['x'] += p['dx']
        p['y'] += p['dy']
        p['lifetime'] -= 1
        if p['lifetime'] > 0:
            alive_particles.append(p)
    return alive_particles

def draw_particles(surface, particles):
    for p in particles:
        alpha = int(255 * (p['lifetime'] / p['max_lifetime']))
        color = list(p['color'])
        color.append(alpha)
        surf = pygame.Surface((p['size'] * 2, p['size'] * 2), pygame.SRCALPHA)
        pygame.draw.circle(surf, color, (p['size'], p['size']), p['size'])
        surface.blit(surf, (p['x'] - p['size'], p['y'] - p['size']))

def show_pause_menu():
    resume_btn = Button(WIDTH // 2 - 150, HEIGHT // 2 - 60, 300, 60, "Resume")
    menu_btn = Button(WIDTH // 2 - 150, HEIGHT // 2 + 20, 300, 60, "Main Menu")
    quit_btn = Button(WIDTH // 2 - 150, HEIGHT // 2 + 100, 300, 60, "Quit")

    overlay = pygame.Surface((WIDTH, HEIGHT))
    overlay.fill((0, 0, 0))
    overlay.set_alpha(128)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return 'resume'

            if resume_btn.handle_event(event):
                return 'resume'
            if menu_btn.handle_event(event):
                return 'menu'
            if quit_btn.handle_event(event):
                pygame.quit()
                sys.exit()

        screen.blit(overlay, (0, 0))
        title = main_font.render("Paused", True, COLORS['text'])
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 4))

        resume_btn.draw(screen)
        menu_btn.draw(screen)
        quit_btn.draw(screen)

        pygame.display.flip()
        clock.tick(FPS)

def main_menu():
    play_btn = Button(WIDTH // 2 - 150, HEIGHT // 2 - 60, 300, 60, "Start Game")
    ai_btn = Button(WIDTH // 2 - 150, HEIGHT // 2 + 20, 300, 60, "AI Mode")
    quit_btn = Button(WIDTH // 2 - 150, HEIGHT // 2 + 100, 300, 60, "Quit")

    particles = []

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if play_btn.handle_event(event):
                return False
            if ai_btn.handle_event(event):
                return True
            if quit_btn.handle_event(event):
                pygame.quit()
                sys.exit()

        if random.random() < 0.1:
            particles.extend(create_particle_effect(
                random.randint(0, WIDTH),
                random.randint(0, HEIGHT),
                COLORS['player'],
                10
            ))

        particles = update_particles(particles)
        screen.fill(COLORS['menu_bg'])
        draw_particles(screen, particles)

        title = main_font.render("Maze Game", True, COLORS['text'])
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 4))

        play_btn.draw(screen)
        ai_btn.draw(screen)
        quit_btn.draw(screen)

        pygame.display.flip()
        clock.tick(FPS)

def game_loop(level, score, use_ai):
    global solution_idx, solution

    grid_size = max(20, 50 - min(level * 3, 40))
    maze, par = generate_maze(level, WIDTH - 2 * PADDING, HEIGHT - 2 * PADDING, grid_size)

    player_pos = [0, 0]
    maze_width, maze_height = len(maze[0]), len(maze)
    exit_pos = [maze_width - 1, maze_height - 1]

    x_offset = (WIDTH - maze_width * grid_size) // 2
    y_offset = (HEIGHT - maze_height * grid_size) // 2

    visited = {(0, 0)}
    moves = 0
    particles = []
    start_time = pygame.time.get_ticks()
    last_move_time = pygame.time.get_ticks()
    move_delay = 300

    back_button = BackButton(20, HEIGHT - 60)

    if use_ai:
        solution = solve_maze(maze)
        solution_idx = 0

    while True:
        current_time = pygame.time.get_ticks()
        clock.tick(FPS) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    result = show_pause_menu()
                    if result == 'menu':
                        return 'menu'
                    start_time = pygame.time.get_ticks() - (current_time - start_time)

            if back_button.handle_event(event):
                return 'menu'

        if current_time - last_move_time >= move_delay:
            player_pos.copy()
            moved = False

            if use_ai and solution_idx < len(solution):
                player_pos = list(solution[solution_idx])
                solution_idx += 1
                moves += 1
                moved = True
            else:
                keys = pygame.key.get_pressed()
                if keys[pygame.K_LEFT] and player_pos[0] > 0 and maze[player_pos[1]][player_pos[0] - 1] == 0:
                    player_pos[0] -= 1
                    moves += 1
                    moved = True
                elif keys[pygame.K_RIGHT] and player_pos[0] < maze_width - 1 and maze[player_pos[1]][player_pos[0] + 1] == 0:
                    player_pos[0] += 1
                    moves += 1
                    moved = True
                elif keys[pygame.K_UP] and player_pos[1] > 0 and maze[player_pos[1] - 1][player_pos[0]] == 0:
                    player_pos[1] -= 1
                    moves += 1
                    moved = True
                elif keys[pygame.K_DOWN] and player_pos[1] < maze_height - 1 and maze[player_pos[1] + 1][player_pos[0]] == 0:
                    player_pos[1] += 1
                    moves += 1
                    moved = True

            if moved:
                last_move_time = current_time
                visited.add(tuple(player_pos))
                particles.extend(create_particle_effect(
                    player_pos[0] * grid_size + x_offset + grid_size // 2,
                    player_pos[1] * grid_size + y_offset + grid_size // 2,
                    COLORS['player'],
                    grid_size // 2
                ))

        particles = update_particles(particles)
        screen.fill(COLORS['background'])

        for y in range(maze_height):
            for x in range(maze_width):
                rect = pygame.Rect(
                    x * grid_size + x_offset,
                    y * grid_size + y_offset,
                    grid_size,
                    grid_size
                )
                if maze[y][x] == 1:
                    pygame.draw.rect(screen, COLORS['wall'], rect)
                else:
                    color = COLORS['visited'] if (x, y) in visited else COLORS['path']
                    pygame.draw.rect(screen, color, rect)
                pygame.draw.rect(screen, (0, 0, 0), rect, 1)

        exit_rect = pygame.Rect(
            exit_pos[0] * grid_size + x_offset,
            exit_pos[1] * grid_size + y_offset,
            grid_size,
            grid_size
        )
        pygame.draw.rect(screen, COLORS['exit'], exit_rect)

        player_rect = pygame.Rect(
            player_pos[0] * grid_size + x_offset,
            player_pos[1] * grid_size + y_offset,
            grid_size,
            grid_size
        )
        pygame.draw.rect(screen, COLORS['player'], player_rect)

        draw_particles(screen, particles)

        elapsed_time = (current_time - start_time) // 1000
        score_value = max(1000 - moves, 0) 

        texts = [
            f"Level: {level}",
            f"Moves: {moves}",
            f"Best Moves: {par}",
            f"Time: {elapsed_time}s",
            f"Score: {score_value}"  
        ]

        for i, text in enumerate(texts):
            surf = game_font.render(text, True, COLORS['text'])
            screen.blit(surf, (20, 20 + i * 40))  

        back_button.draw(screen)

        instructions = [
            "ESC - Pause Menu",
            "Arrow Keys - Move",
            "Back - Return to Menu"
        ]
        instruction_font = pygame.font.Font(None, 24)  # حجم أصغر للخط
        for i, text in enumerate(instructions):
            surf = instruction_font.render(text, True, COLORS['text'])
            screen.blit(surf, (WIDTH - 200, 20 + i * 25))

        pygame.display.flip()

        if player_pos == exit_pos:
            return moves

def solve_maze(maze):
    maze_height, maze_width = maze.shape
    start = (0, 0)
    goal = (maze_height - 1, maze_width - 1)
    queue = deque([start])
    came_from = {start: None}

    while queue:
        x, y = queue.popleft()
        if (x, y) == goal:
            break

        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < maze_width and 0 <= ny < maze_height and maze[ny][nx] == 0:
                if (nx, ny) not in came_from:
                    queue.append((nx, ny))
                    came_from[(nx, ny)] = (x, y)

    path = []
    current = goal
    while current:
        path.append(current)
        current = came_from[current]
    path.reverse()
    return path


def main():
    MAX_LEVEL = 40
    INITIAL_LEVEL = 0

    while True:
        use_ai = main_menu()
        level = INITIAL_LEVEL
        score = 0

        while level <= MAX_LEVEL:
            result = game_loop(level, score, use_ai)
            if result == 'menu':
                break
            score += max(1000 - result, 0)
            level += 1

        if level > MAX_LEVEL:
            print("Congratulations! You've completed the game.")
            return



if __name__ == "__main__":
    main()
