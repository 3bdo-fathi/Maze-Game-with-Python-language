from collections import deque  # هنستورد حاجات هتساعدنا نعمل الجيم
import pygame  # دي المكتبة الي هنرسم بيها الجيم
import random  # عشان نعمل حركات عشوائية وإفكت جميل
from levels import generate_maze  # هنستورد الميتود الي بيولد ليفلات الماز

pygame.init()  # تشغيل pygame وكل حاجة متعلقة بيها
pygame.display.set_caption("Maze Game - EELU")  # عنوان اللعبة

# ألوان الجيم
COLORS = {
    'background': (20, 20, 40),  # لون الخلفية
    'wall': (70, 30, 80),  # لون الجدار
    'path': (200, 220, 255),  # لون الممر
    'player': (255, 160, 0),  # لون اللاعب
    'exit': (50, 220, 100),  # لون المخرج
    'text': (240, 240, 255),  # لون الكتابة
    'visited': (100, 150, 200)  # لون الممرات المتكررة
}

WIDTH, HEIGHT = 1000, 600  # حجم الشاشة ا
PADDING = 30  # من الحواف مسافة

screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.DOUBLEBUF)  # اعمل شاشة الجيم

font = pygame.font.Font(None, 74)  # الخط الكبير - للعناوين
small_font = pygame.font.Font(None, 36)  # الخط الصغير - للتفاصيل

clock = pygame.time.Clock()  # بنتحكم في سرعة الفريمات

DIRECTIONS = [(0, 1), (1, 0), (0, -1), (-1, 0)]  # الاتجاهات


def particle_effect(screen, x, y, color, grid_size):
    # هنعمل إفكت جميل لما اللاعب بيتحرك - زي الفقاعات
    for _ in range(10):
        px = x + random.randint(-grid_size // 2, grid_size // 2)
        py = y + random.randint(-grid_size // 2, grid_size // 2)
        size = random.randint(2, 5)
        pygame.draw.circle(screen, color, (px, py), size)
        pygame.display.update()
        pygame.time.delay(10)


def draw_maze(maze, x_offset, y_offset, visited, grid_size):
    # هنرسم ال maze بتاعنا
    for y in range(len(maze)):
        for x in range(len(maze[0])):
            # لون الخلية تحديد
            if maze[y][x] == 1:
                color = COLORS['wall']
            else:
                color = COLORS['path']

            # لون الخلايا تعديل
            if (x, y) in visited:
                color = tuple(min(255, c + 50) for c in color)

            # رسم الخلية
            pygame.draw.rect(screen, color, (x * grid_size + x_offset, y * grid_size + y_offset, grid_size, grid_size))
            pygame.draw.rect(screen, tuple(max(0, c - 30) for c in color),
                             (x * grid_size + x_offset, y * grid_size + y_offset, grid_size, grid_size), 1)


def draw_text(text, font, color, surface, x, y):
    # هنكتب الكلام في الجيم
    textobj = font.render(text, True, color)
    textrect = textobj.get_rect()
    textrect.topleft = (x, y)
    surface.blit(textobj, textrect)


def main_menu():
    # القائمة الرئيسة - المكان الي هنختار منه نوع الجيم
    while True:
        screen.fill(COLORS['background'])
        draw_text('Maze Game', font, COLORS['text'], screen, WIDTH // 2 - 150, HEIGHT // 2 - 150)
        draw_text('Press 1 to start without AI', small_font, COLORS['text'], screen, WIDTH // 2 - 150, HEIGHT // 2 - 50)
        draw_text('Press 2 to start with AI', small_font, COLORS['text'], screen, WIDTH // 2 - 150, HEIGHT // 2)
        draw_text('Press Q to quit anytime', small_font, COLORS['text'], screen, WIDTH // 2 - 150, HEIGHT // 2 + 50)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    return False  # وضع عادي بدون ذكاء اصطناعي
                elif event.key == pygame.K_2:
                    return True  # مع الذكاء وضع الاصطناعي يحل الماز
                elif event.key == pygame.K_q:
                    pygame.quit()
                    quit()
        pygame.display.update()
        clock.tick(10)


def display_level(level):
    # هنعرض رَقَم الليفل - عشان اللاعب يعرف مكان فين
    screen.fill(COLORS['background'])
    draw_text(f'Level {level}', font, COLORS['text'], screen, WIDTH // 2 - 100, HEIGHT // 2 - 50)
    pygame.display.update()
    pygame.time.wait(2000)


def solve_maze(maze):
    # الذكاء الاصطناعي بيحل ال maze
    maze_height, maze_width = maze.shape
    start = (0, 0)
    goal = (maze_height - 1, maze_width - 1)
    queue = deque([start])
    came_from = {start: None}

    while queue:
        x, y = queue.popleft()
        if (x, y) == goal:
            break

        for dx, dy in DIRECTIONS:
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


def game_loop(level, score, use_ai):
    # دي الدالة الرئيسية للعبة - الحركة والألعاب كلها هنا
    global solution_index, solution_path
    base_grid_size = 50
    grid_size = max(20, base_grid_size - level)

    player_x, player_y = 0, 0
    maze, par = generate_maze(level, WIDTH - 2 * PADDING, HEIGHT - 2 * PADDING, grid_size)
    maze_width, maze_height = len(maze[0]), len(maze)
    x_offset = (WIDTH - maze_width * grid_size) // 2
    y_offset = (HEIGHT - maze_height * grid_size) // 2

    exit_x, exit_y = maze_width - 1, maze_height - 1
    move_count = 0
    visited = set()
    visited.add((player_x, player_y))

    if use_ai:
        solution_path = solve_maze(maze)
        solution_index = 0

    start_time = pygame.time.get_ticks()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    pygame.quit()
                    quit()
                if event.key == pygame.K_m:
                    return 'menu'  # رجوع للقائمة الرئيسية
                if event.key == pygame.K_h:
                    if use_ai:
                        solution_index = 0  # إعادة تشغيل use_ai

        keys = pygame.key.get_pressed()
        moved = False

        if use_ai:
            # الذكاء الاصطناعي
            if solution_index < len(solution_path):
                player_x, player_y = solution_path[solution_index]
                solution_index += 1
                move_count += 1
                moved = True
        else:
            # تحرك يدوي
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                if player_x > 0 and maze[player_y][player_x - 1] == 0:
                    player_x -= 1
                    move_count += 1
                    moved = True
            elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                if player_x < maze_width - 1 and maze[player_y][player_x + 1] == 0:
                    player_x += 1
                    move_count += 1
                    moved = True
            elif keys[pygame.K_UP] or keys[pygame.K_w]:
                if player_y > 0 and maze[player_y - 1][player_x] == 0:
                    player_y -= 1
                    move_count += 1
                    moved = True
            elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
                if player_y < maze_height - 1 and maze[player_y + 1][player_x] == 0:
                    player_y += 1
                    move_count += 1
                    moved = True

        if moved:
            visited.add((player_x, player_y))
            # تأثير جميل لما بتتحرك - زي الفقاعات
            particle_effect(screen,
                            player_x * grid_size + x_offset + grid_size // 2,
                            player_y * grid_size + y_offset + grid_size // 2,
                            COLORS['player'], grid_size)

        screen.fill(COLORS['background'])
        draw_maze(maze, x_offset, y_offset, visited, grid_size)

        # رسم اللاعب والمخرج
        pygame.draw.rect(screen, COLORS['player'],
                         (player_x * grid_size + x_offset, player_y * grid_size + y_offset, grid_size, grid_size))
        pygame.draw.rect(screen, COLORS['exit'],
                         (exit_x * grid_size + x_offset, exit_y * grid_size + y_offset, grid_size, grid_size))

        # الكتابة في الجيم
        draw_text(f'Moves: {move_count}', small_font, COLORS['text'], screen, 10, 10)
        draw_text(f'Best Moves: {par}', small_font, COLORS['text'], screen, 10, 50)
        draw_text(f'Level: {level}', small_font, COLORS['text'], screen, 10, HEIGHT - 40)
        draw_text('Press Q to quit', small_font, COLORS['text'], screen, WIDTH - 210, HEIGHT - 40)
        draw_text('Press M for menu', small_font, COLORS['text'], screen, WIDTH - 210, HEIGHT - 80)


        elapsed_time = (pygame.time.get_ticks() - start_time) // 1000
        draw_text(f'Time: {elapsed_time}s', small_font, COLORS['text'], screen, WIDTH - 150, 50)

        live_score = score + max(1000 - move_count, 0)
        draw_text(f'Score: {live_score}', small_font, COLORS['text'], screen, WIDTH - 150, 10)

        pygame.display.update()
        clock.tick(10)

        if player_x == exit_x and player_y == exit_y:
            running = False

    return move_count


if __name__ == '__main__':
    # نقطة البداية - المكان الي الجيم هيبدأ منه
    while True:
        use_ai = main_menu()  # نختار الوضع
        current_level = 1  # نبدأ من المرحلة الأولى
        total_score = 0  # نبدأ من صفر
        while True:
            display_level(current_level)  # نعرض رقم المرحلة
            result = game_loop(current_level, total_score, use_ai)  # نلعب
            if result == 'menu':
                break  # نرجع للقائمة الرئيسية
            moves = result
            total_score += max(1000 - moves, 0)  # نحسب النقاط
            current_level += 1  # نرفع المرحلة