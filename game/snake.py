import pygame
import random
import sys

pygame.init()

# Constants
WIDTH, HEIGHT = 600, 400
GRID_SIZE = 20
FPS = 10

# Colors
BLACK = (20, 20, 20)
GREEN = (46, 204, 113)
RED = (231, 76, 60)
WHITE = (236, 240, 241)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake")
clock = pygame.time.Clock()

snake = [(100, 100), (80, 100), (60, 100)]
direction = (GRID_SIZE, 0)
food = (random.randrange(0, WIDTH // GRID_SIZE) * GRID_SIZE,
        random.randrange(0, HEIGHT // GRID_SIZE) * GRID_SIZE)
score = 0

font = pygame.font.SysFont("consolas", 20)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and direction != (0, GRID_SIZE):
                direction = (0, -GRID_SIZE)
            elif event.key == pygame.K_DOWN and direction != (0, -GRID_SIZE):
                direction = (0, GRID_SIZE)
            elif event.key == pygame.K_LEFT and direction != (GRID_SIZE, 0):
                direction = (-GRID_SIZE, 0)
            elif event.key == pygame.K_RIGHT and direction != (-GRID_SIZE, 0):
                direction = (GRID_SIZE, 0)

    # Move snake head
    new_head = (snake[0][0] + direction[0], snake[0][1] + direction[1])

    # Check wall collisions
    if not (0 <= new_head[0] < WIDTH and 0 <= new_head[1] < HEIGHT):
        break  # Game Over

    # Check self collision
    if new_head in snake:
        break  # Game Over

    snake.insert(0, new_head)

    # Check food collision
    if new_head == food:
        score += 1
        food = (random.randrange(0, WIDTH // GRID_SIZE) * GRID_SIZE,
                random.randrange(0, HEIGHT // GRID_SIZE) * GRID_SIZE)
    else:
        snake.pop()

    # Draw frame
    screen.fill(BLACK)
    for segment in snake:
        pygame.draw.rect(screen, GREEN, (*segment, GRID_SIZE - 1, GRID_SIZE - 1))
    pygame.draw.rect(screen, RED, (*food, GRID_SIZE - 1, GRID_SIZE - 1))
    
    score_surf = font.render(f"Score: {score}", True, WHITE)
    screen.blit(score_surf, (10, 10))

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()