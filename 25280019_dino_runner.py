import pygame
import sys
import random
import os

# Initialize Pygame
pygame.init()

# Set up some constants
WIDTH, HEIGHT = 800, 400
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DAY_COLOR = (135, 206, 235)
NIGHT_COLOR = (25, 25, 112)
CACTUS_WIDTH, CACTUS_HEIGHT = 50, 50
PTERODACTYL_WIDTH, PTERODACTYL_HEIGHT = 50, 50
DINO_WIDTH, DINO_HEIGHT = 50, 50
GRAVITY = 1
JUMP_VEL = 20
DUCK_VEL = 10
OBSTACLE_VEL = 5
SCORE_FONT = pygame.font.SysFont('Arial', 24)
GAME_OVER_FONT = pygame.font.SysFont('Arial', 48)
HIGH_SCORE_FILE = 'highscore.txt'

class Dino:
    def __init__(self):
        self.x = 100
        self.y = HEIGHT // 2 - DINO_HEIGHT // 2
        self.width = DINO_WIDTH
        self.height = DINO_HEIGHT
        self.velocity = 0
        self.gravity = GRAVITY
        self.is_jumping = False
        self.is_ducking = False

    def jump(self):
        if not self.is_jumping:
            self.velocity = -JUMP_VEL
            self.is_jumping = True

    def fall(self):
        if self.is_jumping:
            self.velocity += self.gravity
            self.y += self.velocity
            if self.y > HEIGHT // 2 - DINO_HEIGHT // 2:
                self.y = HEIGHT // 2 - DINO_HEIGHT // 2
                self.is_jumping = False

    def duck(self):
        if not self.is_ducking:
            self.velocity = DUCK_VEL
            self.is_ducking = True

    def update(self):
        if self.is_jumping:
            self.fall()
        elif self.is_ducking:
            self.y += self.velocity
            if self.y > HEIGHT // 2 - DINO_HEIGHT // 2:
                self.y = HEIGHT // 2 - DINO_HEIGHT // 2
                self.is_ducking = False

class Obstacle:
    def __init__(self, x, y, width, height, type):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.type = type

    def update(self):
        self.x -= OBSTACLE_VEL

    def is_off_screen(self):
        return self.x < -self.width

class Score:
    def __init__(self):
        self.current_score = 0
        self.high_score = self.get_high_score()

    def increment(self):
        self.current_score += 1

    def update_high_score(self):
        if self.current_score > self.high_score:
            self.high_score = self.current_score
            self.save_high_score()

    def get_high_score(self):
        try:
            with open(HIGH_SCORE_FILE, 'r') as f:
                return int(f.read())
        except FileNotFoundError:
            return 0

    def save_high_score(self):
        with open(HIGH_SCORE_FILE, 'w') as f:
            f.write(str(self.high_score))

class Game:
    def __init__(self):
        self.dino = Dino()
        self.obstacles = []
        self.score = Score()
        self.game_active = True
        self.day_night_cycle = True
        self.background_color = DAY_COLOR
        self.cycle_timer = 0
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()

    def update(self):
        if self.game_active:
            self.dino.update()
            for obstacle in self.obstacles:
                obstacle.update()
                if obstacle.is_off_screen():
                    self.obstacles.remove(obstacle)
                if (obstacle.x < self.dino.x + self.dino.width and
                        obstacle.x + obstacle.width > self.dino.x and
                        obstacle.y < self.dino.y + self.dino.height and
                        obstacle.y + obstacle.height > self.dino.y):
                    self.game_active = False
            self.score.increment()
            self.score.update_high_score()
            if random.random() < 0.05:
                self.obstacles.append(Obstacle(WIDTH, HEIGHT // 2 - CACTUS_HEIGHT // 2, CACTUS_WIDTH, CACTUS_HEIGHT, 'cactus'))
            if random.random() < 0.05:
                self.obstacles.append(Obstacle(WIDTH, HEIGHT // 2 - PTERODACTYL_HEIGHT // 2, PTERODACTYL_WIDTH, PTERODACTYL_HEIGHT, 'pterodactyl'))
            self.cycle_timer += 1
            if self.cycle_timer >= 600:
                self.cycle_timer = 0
                if self.background_color == DAY_COLOR:
                    self.background_color = NIGHT_COLOR
                else:
                    self.background_color = DAY_COLOR

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.dino.jump()
                elif event.key == pygame.K_DOWN:
                    self.dino.duck()
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_DOWN:
                    self.dino.is_ducking = False

    def draw(self):
        self.screen.fill(self.background_color)
        for obstacle in self.obstacles:
            if obstacle.type == 'cactus':
                pygame.draw.rect(self.screen, WHITE, (obstacle.x, obstacle.y, obstacle.width, obstacle.height))
            elif obstacle.type == 'pterodactyl':
                pygame.draw.rect(self.screen, WHITE, (obstacle.x, obstacle.y, obstacle.width, obstacle.height))
        pygame.draw.rect(self.screen, WHITE, (self.dino.x, self.dino.y, self.dino.width, self.dino.height))
        score_text = SCORE_FONT.render(f'Score: {self.score.current_score}', True, BLACK)
        self.screen.blit(score_text, (10, 10))
        high_score_text = SCORE_FONT.render(f'High Score: {self.score.high_score}', True, BLACK)
        self.screen.blit(high_score_text, (10, 30))
        if not self.game_active:
            game_over_text = GAME_OVER_FONT.render('Game Over', True, BLACK)
            self.screen.blit(game_over_text, (WIDTH // 2 - 100, HEIGHT // 2 - 50))
            restart_text = SCORE_FONT.render('Press Space to restart', True, BLACK)
            self.screen.blit(restart_text, (WIDTH // 2 - 100, HEIGHT // 2))
        pygame.display.flip()

    def run(self):
        while True:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(60)

if __name__ == '__main__':
    game = Game()
    game.run()