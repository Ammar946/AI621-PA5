import pygame
import sys
import random
import os

# Initialize Pygame
pygame.init()

# Set up screen constants
WIDTH, HEIGHT = 800, 400
GROUND_Y = HEIGHT - 50

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DAY_COLOR = (135, 206, 235)      # Sky blue
NIGHT_COLOR = (25, 25, 112)      # Midnight blue
GREEN = (46, 204, 113)           # Green cacti
RED = (231, 76, 60)             # Red pterodactyls
GREY = (127, 140, 141)          # Grey Dino

# Dimensions
DINO_WIDTH = 40
DINO_STAND_HEIGHT = 50
DINO_DUCK_HEIGHT = 25

CACTUS_WIDTH = 25
CACTUS_HEIGHT = 45

PTERODACTYL_WIDTH = 40
PTERODACTYL_HEIGHT = 30

# Speed settings
INITIAL_SPEED = 5
MAX_SPEED = 15

# Fonts
SCORE_FONT = pygame.font.SysFont('Arial', 24)
GAME_OVER_FONT = pygame.font.SysFont('Arial', 48)

HIGH_SCORE_FILE = 'highscore.txt'

class Dino:
    def __init__(self):
        self.width = DINO_WIDTH
        self.height = DINO_STAND_HEIGHT
        self.x = 100
        self.y = GROUND_Y - self.height
        
        self.velocity = 0
        self.gravity = 0.8
        self.jump_vel = -14
        
        self.is_jumping = False
        self.is_ducking = False

    def jump(self):
        if not self.is_jumping and not self.is_ducking:
            self.velocity = self.jump_vel
            self.is_jumping = True

    def duck(self):
        if not self.is_jumping:
            self.is_ducking = True
            self.height = DINO_DUCK_HEIGHT
            self.y = GROUND_Y - self.height

    def stand(self):
        self.is_ducking = False
        self.height = DINO_STAND_HEIGHT
        self.y = GROUND_Y - self.height

    def update(self):
        if self.is_jumping:
            self.velocity += self.gravity
            self.y += self.velocity
            
            # Check landing
            if self.y >= GROUND_Y - self.height:
                self.y = GROUND_Y - self.height
                self.is_jumping = False
                self.velocity = 0

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def draw(self, screen):
        pygame.draw.rect(screen, GREY, self.get_rect())


class Obstacle:
    def __init__(self, x, y, width, height, type):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.type = type
        self.passed = False

    def update(self, speed):
        self.x -= speed

    def is_off_screen(self):
        return self.x < -self.width

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def draw(self, screen):
        color = GREEN if self.type == 'cactus' else RED
        pygame.draw.rect(screen, color, self.get_rect())


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
            if os.path.exists(HIGH_SCORE_FILE):
                with open(HIGH_SCORE_FILE, 'r') as f:
                    content = f.read().strip()
                    return int(content) if content else 0
        except Exception:
            pass
        return 0

    def save_high_score(self):
        try:
            with open(HIGH_SCORE_FILE, 'w') as f:
                f.write(str(self.high_score))
        except Exception:
            pass


class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("PA5 Dino Runner")
        self.clock = pygame.time.Clock()
        
        self.background_color = DAY_COLOR
        self.cycle_timer = 0
        
        # Setup Pygame Custom Timer Event for Obstacle Spawning
        self.SPAWN_EVENT = pygame.USEREVENT + 1
        pygame.time.set_timer(self.SPAWN_EVENT, 1800) # Every 1.8 seconds initially
        
        self.reset()

    def reset(self):
        self.dino = Dino()
        self.obstacles = []
        self.score = Score()
        self.game_active = True
        self.speed = INITIAL_SPEED

    def spawn_obstacle(self):
        # Prevent spawning if game is not active
        if not self.game_active:
            return

        # Randomize obstacle type (Cactus vs Pterodactyl)
        if random.random() < 0.65:
            # Spawn Cactus with Clustering (1 to 3 items)
            cluster_size = random.randint(1, 3)
            width = CACTUS_WIDTH * cluster_size
            height = CACTUS_HEIGHT
            y = GROUND_Y - height
            self.obstacles.append(Obstacle(WIDTH, y, width, height, 'cactus'))
        else:
            # Spawn Pterodactyl flying at low or medium heights
            # y_pos is high enough to duck under, or low enough to jump over
            y_pos = random.choice([GROUND_Y - 75, GROUND_Y - 45])
            self.obstacles.append(Obstacle(WIDTH, y_pos, PTERODACTYL_WIDTH, PTERODACTYL_HEIGHT, 'pterodactyl'))
            
        # Dynamically change the next timer interval slightly to prevent static rhythmic spacing
        next_interval = random.randint(1200, 2400)
        pygame.time.set_timer(self.SPAWN_EVENT, next_interval)

    def update(self):
        if self.game_active:
            # Update Day/Night background cycle
            self.cycle_timer += 1
            if self.cycle_timer >= 600:  # Alternate background every 10 seconds (600 frames)
                self.cycle_timer = 0
                self.background_color = NIGHT_COLOR if self.background_color == DAY_COLOR else DAY_COLOR
            
            # Update Dino
            self.dino.update()
            
            # Gradually increase game speed as score increments
            self.speed = min(INITIAL_SPEED + (self.score.current_score // 5), MAX_SPEED)
            
            # Update Obstacles
            for obstacle in list(self.obstacles):
                obstacle.update(self.speed)
                
                # Check for successful pass (when obstacle is completely behind Dino)
                if not obstacle.passed and (obstacle.x + obstacle.width) < self.dino.x:
                    obstacle.passed = True
                    self.score.increment()
                    self.score.update_high_score()
                
                # Remove offscreen obstacles
                if obstacle.is_off_screen():
                    self.obstacles.remove(obstacle)
                
                # Check Collisions
                if self.dino.get_rect().colliderect(obstacle.get_rect()):
                    self.game_active = False

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            elif event.type == self.SPAWN_EVENT:
                self.spawn_obstacle()
                
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if self.game_active:
                        self.dino.jump()
                    else:
                        self.reset()  # Triggers a perfect reset on SPACE
                elif event.key == pygame.K_DOWN:
                    if self.game_active:
                        self.dino.duck()
                        
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_DOWN:
                    if self.game_active:
                        self.dino.stand()

    def draw(self):
        self.screen.fill(self.background_color)
        
        # Draw Ground Line
        line_color = WHITE if self.background_color == NIGHT_COLOR else BLACK
        pygame.draw.line(self.screen, line_color, (0, GROUND_Y), (WIDTH, GROUND_Y), 3)
        
        # Draw Entities
        self.dino.draw(self.screen)
        for obstacle in self.obstacles:
            obstacle.draw(self.screen)
            
        # Draw HUD texts
        text_color = WHITE if self.background_color == NIGHT_COLOR else BLACK
        
        score_text = SCORE_FONT.render(f"Score: {self.score.current_score}", True, text_color)
        self.screen.blit(score_text, (20, 20))
        
        hi_score_text = SCORE_FONT.render(f"HI: {self.score.high_score}", True, text_color)
        self.screen.blit(hi_score_text, (WIDTH - 120, 20))
        
        if not self.game_active:
            # Draw Game Over overlay
            go_text = GAME_OVER_FONT.render("GAME OVER", True, RED)
            restart_text = SCORE_FONT.render("Press SPACE to Restart", True, text_color)
            
            # Position overlays centrally
            self.screen.blit(go_text, (WIDTH // 2 - go_text.get_width() // 2, HEIGHT // 2 - 50))
            self.screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2 + 10))

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