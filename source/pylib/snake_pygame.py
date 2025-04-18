import pygame
import random
import time

# 초기 설정
pygame.init()
WIDTH, HEIGHT = 600, 400
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("다수 먹이 스네이크 🐍🍎")

# 색깔
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
WHITE = (255, 255, 255)

# 변수 설정
clock = pygame.time.Clock()
snake_block = 20
snake_speed = 10
font = pygame.font.SysFont(None, 35)

# 점수 출력 함수
def show_score(score):
    text = font.render(f"점수: {score}", True, WHITE)
    win.blit(text, [10, 10])

# 뱀 그리기 함수
def draw_snake(snake_list):
    for x, y in snake_list:
        pygame.draw.rect(win, GREEN, [x, y, snake_block, snake_block])

# 먹이 초기화 함수
def spawn_foods(count):
    return [
        [
            random.randrange(0, WIDTH - snake_block, snake_block),
            random.randrange(0, HEIGHT - snake_block, snake_block)
        ]
        for _ in range(count)
    ]

def game_loop():
    game_over = False
    x, y = WIDTH // 2, HEIGHT // 2
    dx, dy = 0, 0

    snake_list = []
    snake_length = 1
    score = 0

#####################################################
    food_count = 5
    foods = spawn_foods(food_count)

    while not game_over:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    dx, dy = -snake_block, 0
                elif event.key == pygame.K_RIGHT:
                    dx, dy = snake_block, 0
                elif event.key == pygame.K_UP:
                    dx, dy = 0, -snake_block
                elif event.key == pygame.K_DOWN:
                    dx, dy = 0, snake_block

        x += dx
        y += dy

        if x < 0 or x >= WIDTH or y < 0 or y >= HEIGHT:
            game_over = True

        win.fill(BLACK)

        # 먹이 그리기
        for fx, fy in foods:
            pygame.draw.rect(win, RED, [fx, fy, snake_block, snake_block])

        # 뱀 위치 업데이트
        head = [x, y]
        snake_list.append(head)
        if len(snake_list) > snake_length:
            del snake_list[0]

        # 자기 몸에 부딪히면 게임오버
        for segment in snake_list[:-1]:
            if segment == head:
                game_over = True

        draw_snake(snake_list)
        show_score(score)
        pygame.display.update()

        # 먹이 먹기
        for food in foods[:]:
            if x == food[0] and y == food[1]:
                foods.remove(food)
                snake_length += 1
                score += 10
                foods.append([
                    random.randrange(0, WIDTH - snake_block, snake_block),
                    random.randrange(0, HEIGHT - snake_block, snake_block)
                ])

        clock.tick(snake_speed)

    time.sleep(2)
    pygame.quit()

game_loop()