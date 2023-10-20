import pygame, random, sys
from pygame.locals import QUIT, KEYDOWN, K_LEFT, K_RIGHT, K_SPACE
from button import Button

pygame.init()

# Constants
WIDTH = 800
HEIGHT = 600
PLAYER_SPEED = 5
PLAYER_HP = 100
BULLET_SPEED = 10
BULLET_DAMAGE = 2
ENEMY_SPAWN_RATE = 30 # 1 in 30 chance of spawning an enemy each frame

COIN_SPEED = 2
COIN_SIZE = 20
SHOP_ITEMS = {
    'health_upgrade': {'cost': 25, 'description': 'Increase Max Health'},
    'power_bullet': {'cost': 50, 'description': 'Increase Bullet Damage'},
    'rapid_fire': {'cost': 75, 'description': 'Increase Fire Rate'},
    'speed_upgrade': {'cost': 30, 'description': 'Increase Ship Speed'}
}
ITEM_HEIGHT = 40
ITEM_WIDTH = 400
ITEM_START_Y = 50
ITEM_START_X = 50

# Menu Constants
MENU_FONT_SIZE = 50
MENU_START_Y = 50
MENU_SPACING = 100
MENU_OPTIONS = ["Start Game", "Quit"]


class MainMenu:
    def __init__(self, game):
        self.game = game
        self.font = pygame.font.SysFont('Arial', MENU_FONT_SIZE)
        self.bg = pygame.image.load("bg.png")
        self.bg = pygame.transform.scale(self.bg, (WIDTH, HEIGHT))
        

    def display(self):
        menu_open = True
        while menu_open:
            start_button = Button(None, (WIDTH // 2, MENU_START_Y), "Start Game", self.font, (255, 255, 255), (200, 200, 200))
            quit_button = Button(None, (WIDTH // 2, MENU_START_Y + MENU_SPACING), "Quit", self.font, (255, 255, 255), (200, 200, 200))
            mouse_position = pygame.mouse.get_pos()
            self.game.screen.blit(self.bg, (0, 0))
            
            for button in [start_button, quit_button]:
                button.check_hover(mouse_position)
                button.update(self.game.screen)
                
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if start_button.check_input(mouse_position):
                        menu_open = False
                        game_instance.run()
                    elif quit_button.check_input(mouse_position):
                        pygame.quit()
                        sys.exit()

            pygame.display.flip()

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Space Shooter")
        pygame.mixer.init()
        self.clock = pygame.time.Clock()
        self.player = Player()
        self.running = True
        self.bullets = []
        self.enemies = []
        self.coins = []
        self.score = 0
        self.total_coins = 0
        self.boss_count = 0
        self.shop = Shop()
        self.shoot_sound = pygame.mixer.Sound("pew.mp3")
        self.shoot_sound.set_volume(0.1)
        self.music = pygame.mixer.music.load("normal_music.wav")
        self.hit_sound = pygame.mixer.Sound("hit.mp3")

    def run(self):
        pygame.mixer.music.play(-1)
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(60)
        pygame.quit()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                self.running = False
            elif event.type == KEYDOWN:
                if event.key == K_SPACE:
                    self.shoot_sound.play()
                    bullet = Bullet(self.player.x + self.player.width // 2, self.player.y)
                    self.bullets.append(bullet)
                elif event.key == pygame.K_ESCAPE:
                    # Open the shop
                    self.open_shop()

    def open_shop(self):
        feedback_msg = ""  # Initialize feedback_msg to an empty string
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == KEYDOWN and event.key == pygame.K_ESCAPE:
                    return
            self.screen.fill((0, 0, 0))
            y_position = ITEM_START_Y
            mouse_x, mouse_y = pygame.mouse.get_pos()
            selected_item = None
            for item, data in SHOP_ITEMS.items():
                if ITEM_START_X < mouse_x < ITEM_START_X + ITEM_WIDTH and y_position < mouse_y < y_position + ITEM_HEIGHT:
                    color = (200, 200, 200)  # Light gray for hover effect
                    selected_item = item
                    if pygame.mouse.get_pressed()[0]:
                        if self.shop.purchase(item, self.player, self):
                            feedback_msg = "Purchase successful!"
                        else:
                            feedback_msg = "Not enough coins!"
                else:
                    color = (255, 255, 255)
                text = f"{data['description']} - {data['cost']} coins"
                label = pygame.font.SysFont('Arial', 25).render(text, True, color)
                self.screen.blit(label, (ITEM_START_X, y_position))
                y_position += ITEM_HEIGHT

            # Display feedback message if any
            if feedback_msg:
                feedback_label = pygame.font.SysFont('Arial', 25).render(feedback_msg, True, (255, 0, 0))
                self.screen.blit(feedback_label, (WIDTH // 2 - 100, HEIGHT - 50))

            # Display total coins
            coins_label = pygame.font.SysFont('Arial', 25).render(f"Total Coins: {self.total_coins}", True, (255, 255, 255))
            self.screen.blit(coins_label, (WIDTH // 2 - 100, 10))

            # Exit button
            exit_button = Button(None, (WIDTH // 2, HEIGHT - 100), "Exit Game", pygame.font.SysFont('Arial', 25), (255, 255, 255), (200, 200, 200))
            exit_button.check_hover((mouse_x, mouse_y))
            exit_button.update(self.screen)
            if exit_button.check_input((mouse_x, mouse_y)):
                if pygame.mouse.get_pressed()[0]:
                    sys.exit()

            pygame.display.flip()
            self.clock.tick(60)

    def display_results(self):
        # Display results
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == KEYDOWN and event.key == pygame.K_ESCAPE:
                    return self.restart()
            self.screen.fill((0, 0, 0))
            text = f"Game Over! Your score is {self.score}"
            label = pygame.font.SysFont('Arial', 25).render(text, True, (255, 255, 255))
            self.screen.blit(label, (WIDTH // 2 - 100, HEIGHT // 2))
            text2 = "Press ESC to restart"
            label2 = pygame.font.SysFont('Arial', 25).render(text2, True, (255, 255, 255))
            self.screen.blit(label2, (WIDTH // 2 - 100, HEIGHT // 2 + 50))
            pygame.display.flip()
            self.clock.tick(60)


    # Restart the game
    def restart(self):
        self.player.reset()
        self.bullets = []
        self.enemies = []
        self.coins = []
        self.total_coins = 0
        self.score = 0

    def update(self):
        # Player Update
        self.player.update()
        if self.player.hp <= 0:
            self.display_results()

        # Bullet Update
        for bullet in self.bullets[:]:
            bullet.update()
            if bullet.y < 0:
                self.bullets.remove(bullet)
            

        # Enemy Spawning and Update
        if random.randint(1, ENEMY_SPAWN_RATE) == 1:
            enemy_type = random.choice(["standard", "speedy", "tank"])
            enemy = Enemy(enemy_type)
            self.enemies.append(enemy)
            
            if self.boss_count // 10 == 1:
                enemy_type = "boss"
                enemy = Enemy(enemy_type)
                self.enemies.append(enemy)
                self.boss_count = 0

        for enemy in self.enemies[:]:
            enemy.update()
            if enemy.y > HEIGHT:
                self.enemies.remove(enemy)

        # Collision Detection (Bullet & Enemy)
        for bullet in self.bullets[:]:
            for enemy in self.enemies[:]:
                if bullet.collides_with(enemy):
                    enemy.hp -= BULLET_DAMAGE
                    if bullet in self.bullets:
                        self.bullets.remove(bullet)
                    if enemy.hp <= 0:
                        coin = Coin(enemy.x + enemy.width // 2, enemy.y)
                        self.boss_count += 1
                        self.score += 1
                        self.coins.append(coin)
                        self.enemies.remove(enemy)

        # Collision Detection (Player & Enemy)
        for enemy in self.enemies[:]:
            if self.player.collides_with_enemy(enemy):
                self.enemies.remove(enemy)
                self.hit_sound.play()
                self.player.hp -= 10

        
        # Coin Update
        for coin in self.coins[:]:
            coin.update()
            if coin.y > HEIGHT:
                self.coins.remove(coin)
            elif self.player.collides_with_coin(coin):
                self.coins.remove(coin)
                self.total_coins += 1

    def draw(self):
        self.screen.fill((0, 0, 0))
        self.player.draw(self.screen)

        # Draw score
        score_text = pygame.font.SysFont('Arial', 20).render(f"Score: {self.score}", True, (255, 255, 255))
        self.screen.blit(score_text, (WIDTH - 100, 10))
        coins_text = pygame.font.SysFont('Arial', 20).render(f"Coins: {self.total_coins}", True, (255, 255, 255))
        self.screen.blit(coins_text, (WIDTH - 100, 30))

        for bullet in self.bullets:
            bullet.draw(self.screen)

        # Draw enemies
        for enemy in self.enemies:
            enemy.draw(self.screen)

        # Draw coins
        for coin in self.coins:
            coin.draw(self.screen)

        pygame.display.flip()

class Coin:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = COIN_SPEED
        self.size = COIN_SIZE
        self.coin_img = pygame.image.load("coin.png")
        self.coin_img = pygame.transform.scale(self.coin_img, (COIN_SIZE, COIN_SIZE))

    def update(self):
        self.y += self.speed

    def draw(self, screen):
        screen.blit(self.coin_img, (self.x, self.y))

class Shop:
    def __init__(self):
        # Pricing for shop items (can be adjusted as needed)
        self.prices = {
            'health_upgrade': 25,
            'power_bullet': 50,
            'rapid_fire': 75,
            'speed_upgrade': 30
        }

    def can_purchase(self, item, coins):
        return coins >= self.prices[item]

    def purchase(self, item, player, game):
        if not self.can_purchase(item, game.total_coins):
            return False

        if item == 'health_upgrade':
            player.max_hp += 20
            player.hp += 20
            print(player.max_hp)
        elif item == 'power_bullet':
            Bullet.DAMAGE += 1
        elif item == 'rapid_fire':
            player.shoot_delay -= 5  # Decrease delay for faster shooting
        elif item == 'speed_upgrade':
            player.speed += 1

        game.total_coins -= self.prices[item]

        return True

class Bullet:
    DAMAGE = 2
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = BULLET_SPEED
        self.width = 5
        self.height = 10

    def update(self):
        self.y -= self.speed

    def draw(self, screen):
        pygame.draw.rect(screen, (255, 255, 0), (self.x, self.y, self.width, self.height))

    def collides_with(self, enemy):
        return (self.x < enemy.x + enemy.width and
                self.x + self.width > enemy.x and
                self.y < enemy.y + enemy.height and
                self.y + self.height > enemy.y)

class Enemy:
    def __init__(self, enemy_type):
        self.width = 50
        self.height = 30
        self.x = random.randint(0, WIDTH - self.width)
        self.y = 0 - self.height
        self.enemy_type = enemy_type
        self.enemy_img = None

        if self.enemy_type == "standard":
            self.speed = 2
            self.color = (255, 0, 0)
            self.hp = 2
            self.enemy_img = pygame.image.load("meteo.png")
            self.enemy_img = pygame.transform.scale(self.enemy_img, (self.width, self.height))
        elif self.enemy_type == "speedy":
            self.speed = 5
            self.color = (255, 165, 0)
            self.hp = 1
            self.enemy_img = pygame.image.load("meteo.png")
            self.enemy_img = pygame.transform.scale(self.enemy_img, (self.width, self.height))
        elif self.enemy_type == "tank":
            self.speed = 1
            self.color = (0, 0, 255)
            self.hp = 10
            self.enemy_img = pygame.image.load("meteo.png")
            self.enemy_img = pygame.transform.scale(self.enemy_img, (self.width, self.height))
        elif self.enemy_type == "boss":
            self.speed = 1
            self.color = (255, 0, 255)
            self.hp = 20
            self.width = 100
            self.height = 100
            self.enemy_img = pygame.image.load("enim.png")
            self.enemy_img = pygame.transform.scale(self.enemy_img, (self.width, self.height))

    def collides_with_bullet(self, bullet):
        return (self.x < bullet.x + bullet.width and
                self.x + self.width > bullet.x and
                self.y < bullet.y + bullet.height and
                self.y + self.height > bullet.y)

    def update(self):
        self.y += self.speed

    def draw(self, screen):
        # pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
        screen.blit(self.enemy_img, (self.x, self.y))


class Player:
    def __init__(self):
        self.x = WIDTH // 2
        self.y = HEIGHT - 50
        self.width = 50
        self.height = 30
        self.speed = PLAYER_SPEED
        self.max_hp = PLAYER_HP
        self.hp = self.max_hp
        self.player_image = pygame.image.load("player2.png")
        self.player_image = pygame.transform.scale(self.player_image, (self.width, self.height))

    def collides_with_coin(self, coin):
        return (self.x < coin.x + coin.size and
                self.x + self.width > coin.x and
                self.y < coin.y + coin.size and
                self.y + self.height > coin.y)
    
    def collides_with_enemy(self, enemy):
        return (self.x < enemy.x + enemy.width and
                self.x + self.width > enemy.x and
                self.y < enemy.y + enemy.height and
                self.y + self.height > enemy.y)
    
    def reset(self):
        self.x = WIDTH // 2
        self.y = HEIGHT - 50
        self.hp = PLAYER_HP

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[K_LEFT]:
            self.x -= self.speed
        if keys[K_RIGHT]:
            self.x += self.speed

    def draw(self, screen):
        # pygame.draw.rect(screen, (0, 255, 0), (self.x, self.y, self.width, self.height))
        screen.blit(self.player_image, (self.x, self.y))
        pygame.draw.rect(screen, (255, 0, 0), (10, 10, 100, 10))
        pygame.draw.rect(screen, (0, 255, 0), (10, 10, self.hp, 10))
        # display hp as text
        hp_text = pygame.font.SysFont('Arial', 20).render(f"HP: {self.hp}", True, (255, 255, 255))
        screen.blit(hp_text, (10, 30))

if __name__ == "__main__":
    game_instance = Game()
    main_menu = MainMenu(game_instance)
    main_menu.display()
