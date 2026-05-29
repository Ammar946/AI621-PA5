import pygame
import sys
import random
import os

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 400
FPS = 60

# Colors
SKY_BLUE = (135, 206, 235)
MIDNIGHT_BLUE = (25, 25, 112)

# Events
SPAWN_OBSTACLE = pygame.USEREVENT + 1

class Dino:
    def __init__(self):
        self.width = 40
        self.height = 50
        self.x = 50
        self.y = SCREEN_HEIGHT - self.height
        self.velocity = 0
        self.gravity = 1

    def update(self):
        self.velocity += self.gravity
        self.y += self.velocity
        ground_y = SCREEN_HEIGHT - self.height
        if self.y >= ground_y:
            self.y = ground_y
            self.velocity = 0

    def jump(self):
        if self.y == SCREEN_HEIGHT - self.height:
            self.velocity = -15

    def duck(self):
        self.height = 25

    def stand(self):
        self.height = 50

    def draw(self, screen):
        pygame.draw.rect(screen, (100, 100, 100), (self.x, self.y, self.width, self.height))

class Obstacle(pygame.Rect):
    def __init__(self, x, y, width, height, color):
        super().__init__(x, y, width, height)
        self.color = color
        self.passed = False

    def update(self, speed):
        self.x -= speed

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self)

class Cactus(Obstacle):
    def __init__(self, x, screen_height):
        super().__init__(x, screen_height-40, 30, 40, (0, 150, 0))

class Pterodactyl(Obstacle):
    def __init__(self, x, screen_height):
        super().__init__(x, random.choice([screen_height-150, screen_height-100, screen_height-70]), 50, 30, (200, 0, 0))

class Score:
    def __init__(self):
        self.current_score = 0
        self.high_score = self.load_high_score()

    def load_high_score(self):
        try:
            with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'highscore.txt'), 'r') as f:
                return int(f.read().strip())
        except (FileNotFoundError, ValueError):
            return 0

    def save_high_score(self):
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'highscore.txt'), 'w') as f:
            f.write(str(self.high_score))

    def update(self, obstacles, dino):
        for obstacle in obstacles:
            if not obstacle.passed and obstacle.x + obstacle.width < dino.x:
                obstacle.passed = True
                self.current_score += 1
        if self.current_score > self.high_score:
            self.high_score = self.current_score
            self.save_high_score()

    def reset(self):
        self.current_score = 0

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.dino = Dino()
        self.obstacles = []
        self.score = Score()
        self.speed = 6
        self.game_active = True
        self.frame_count = 0
        pygame.time.set_timer(SPAWN_OBSTACLE, 2000)

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.score.save_high_score()
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if not self.game_active:
                        if event.key == pygame.K_SPACE:
                            self.reset()
                    else:
                        if event.key == pygame.K_SPACE or event.key == pygame.K_UP:
                            self.dino.jump()
                        elif event.key == pygame.K_DOWN:
                            self.dino.duck()
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_DOWN:
                        self.dino.stand()
                if event.type == SPAWN_OBSTACLE and self.game_active:
                    obstacle_type = random.choice(['cactus', 'pterodactyl'])
                    if obstacle_type == 'cactus':
                        cluster_size = random.randint(1, 3)
                        for i in range(cluster_size):
                            self.obstacles.append(Cactus(SCREEN_WIDTH + i * 35, SCREEN_HEIGHT))
                    else:
                        self.obstacles.append(Pterodactyl(SCREEN_WIDTH, SCREEN_HEIGHT))

            if self.game_active:
                self.dino.update()
                for obstacle in self.obstacles:
                    obstacle.update(self.speed)
                self.obstacles = [obs for obs in self.obstacles if obs.x + obs.width > 0]
                self.score.update(self.obstacles, self.dino)
                self.speed = min(15, 6 + (self.score.current_score / 15.0))

                for obstacle in self.obstacles:
                    dino_rect = pygame.Rect(self.dino.x, self.dino.y, self.dino.width, self.dino.height)
                    if dino_rect.colliderect(obstacle):
                        self.game_active = False
                        self.score.save_high_score()

                self.frame_count += 1
                if self.frame_count > 300:
                    self.frame_count = 0

            if self.frame_count < 150:
                self.screen.fill(SKY_BLUE)
            else:
                self.screen.fill(MIDNIGHT_BLUE)

            if self.game_active:
                self.dino.draw(self.screen)
                for obstacle in self.obstacles:
                    obstacle.draw(self.screen)
                score_text = self.font.render(f'Score: {self.score.current_score}  HI: {self.score.high_score}', True, (255, 255, 255))
                self.screen.blit(score_text, (10, 10))
            else:
                game_over_text = self.font.render('GAME OVER', True, (255, 0, 0))
                self.screen.blit(game_over_text, (SCREEN_WIDTH // 2 - 75, SCREEN_HEIGHT // 2 - 18))
                score_text = self.font.render(f'Score: {self.score.current_score}, High Score: {self.score.high_score}', True, (255, 255, 255))
                self.screen.blit(score_text, (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 + 18))
                press_space_text = self.font.render('Press SPACE to restart', True, (255, 255, 255))
                self.screen.blit(press_space_text, (SCREEN_WIDTH // 2 - 120, SCREEN_HEIGHT // 2 + 60))

            pygame.display.flip()
            self.clock.tick(FPS)

    def reset(self):
        self.dino = Dino()
        self.obstacles = []
        self.score.reset()
        self.speed = 6
        self.game_active = True
        self.frame_count = 0

if __name__ == '__main__':
    game = Game()
    game.run()