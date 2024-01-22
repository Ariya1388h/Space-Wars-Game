import pygame, random

#Initialize pygame
pygame.mixer.pre_init(44100, 16, 2, 4096)
pygame.init()

#Set display surface
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Space Wars")

#Set FPS & clock
FPS = 60
clock = pygame.time.Clock()

round_value = 0

#Define classes
class Game(pygame.sprite.Sprite):
    """A class to control the main game"""

    def __init__(self, player, enemy_group, plaser, elaser):
        global round_value
        self.round_num = 1
        round_value = self.round_num
        self.score = 0

        self.player = player
        self.enemy_group = enemy_group
        self.plaser_group = plaser_group
        self.elaser_group = elaser_group

        self.round_sound = pygame.mixer.Sound("Assets/Sounds/Round.mp3")
        self.startup_sound = pygame.mixer.Sound("Assets/Sounds/Startup.mp3")
        self.breach_sound = pygame.mixer.Sound("Assets/Sounds/Breach.mp3")
        self.enemy_hit_sound = pygame.mixer.Sound("Assets/Sounds/Enemy_hit.mp3")
        self.player_hit_sound = pygame.mixer.Sound("Assets/Sounds/Game_over.mp3 ")
        self.breach_sound.set_volume(0.2)
        self.enemy_hit_sound.set_volume(0.1)
        self.player_hit_sound.set_volume(0.4)

        self.font = pygame.font.Font("Assets/Fonts/AstroSpace.ttf", 32)

    def update(self):
        self.shift_enemys()
        self.collisions()
        self.check_round()

    def draw(self):
        WHITE = (255,255,255)
        
        score_txt = self.font.render("Score: " + str(self.score), True, WHITE)
        score_rect = score_txt.get_rect()
        score_rect.centerx =  WINDOW_WIDTH//2
        score_rect.top = 10

        round_txt = self.font.render("Round " + str(self.round_num), True, WHITE)
        round_rect = round_txt.get_rect()
        round_rect.topleft = (20, 10)

        lives_txt = self.font.render("Lives  " + str(self.player.lives), True, WHITE)
        lives_rect = lives_txt.get_rect()
        lives_rect.topright = (WINDOW_WIDTH - 20, 10)


        screen.blit(score_txt, score_rect)
        screen.blit(round_txt, round_rect)
        screen.blit(lives_txt, lives_rect)
        pygame.draw.line(screen, WHITE, (0, 50), (WINDOW_WIDTH, 50), 5)
        pygame.draw.line(screen, WHITE, (0, WINDOW_HEIGHT - 150), (WINDOW_WIDTH, WINDOW_HEIGHT - 150), 5)

    def shift_enemys(self):
        shift = False
        for enemy in (self.enemy_group.sprites()):
            if enemy.rect.left <= 0 or enemy.rect.right >= WINDOW_WIDTH:
                shift = True

        if shift:
            breach = False
            for enemy in (self.enemy_group.sprites()):
                enemy.rect.y += 10*self.round_num

                enemy.direction = -1*enemy.direction
                enemy.rect.x += enemy.direction*enemy.velocity

                if enemy.rect.bottom >= WINDOW_HEIGHT - 150:
                    breach = True

            if breach:
                self.breach_sound.play()
                self.player.lives -= 1
                self.check_game("GAME OVER! Aliens breached the line", "Continue The Game By Pressing 'Enter'")

    def collisions(self):
        if pygame.sprite.groupcollide(self.plaser_group, self.enemy_group, True, True):
            self.enemy_hit_sound.play()
            self.score += 100

        if pygame.sprite.spritecollide(self.player, self.elaser_group, True):
            self.player_hit_sound.play()
            self.player.lives -= 1

            self.check_game("You DIED", "Continue By Pressing 'Enter'")

    def new_round(self):
        for i in range(11):
            for j in range(5):
                enemy = Enemy(64+i*64, 64+j*64, self.round_num, self.elaser_group)
                self.enemy_group.add(enemy)

        if self.round_num > 1: 
            self.round_sound.play()
        elif self.round_num < 2:
            self.startup_sound.play()
        self.pause("Space Wars, Round " + str(self.round_num), "Press 'ENTER' To play")
    
    def check_round(self):
        if not (self.enemy_group):
            self.score += 1000*self.round_num
            self.round_num += 1
            self.new_round()
    
    def check_game(self, main_txt, sub_txt):
        self.elaser_group.empty()
        self.plaser_group.empty()
        self.player.reset()
        for enemy in self.enemy_group:
            enemy.reset()

        if self.player.lives == 0:
            self.reset()
        else:
            self.pause(main_txt, sub_txt)
    
    def pause(self, main_txt, sub_txt):
        WHITE = (255,255,255)
        BLACK = (0,0,0)

        main_txt = self.font.render(main_txt, True, WHITE)
        main_txt_rect = main_txt.get_rect()
        main_txt_rect.center = (WINDOW_WIDTH//2, WINDOW_HEIGHT//2)
        sub_txt = self.font.render(sub_txt, True, WHITE)
        sub_txt_rect = sub_txt.get_rect()
        sub_txt_rect.center = (WINDOW_WIDTH//2, WINDOW_HEIGHT//2 + 64)

        screen.fill(BLACK)
        screen.blit(main_txt, main_txt_rect)
        screen.blit(sub_txt, sub_txt_rect)
        pygame.display.update()

        global running

        paused = True
        while paused:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        paused = False
                if event.type == pygame.QUIT:
                    paused = False
                    running = False
    
    def reset(self):
        self.pause("Final_score: " + str(self.score), "Continue The Game By Pressing 'Enter'")

        self.score = 0
        self.round_num = 1
        self.player.lives = 5

        self.enemy_group.empty()
        self.elaser_group.empty()
        self.laser_group.empty()

        self.new_round()

class Player(pygame.sprite.Sprite):
    """A class to control the player"""

    def __init__(self, plaser_group):
        super().__init__()

        self.image = pygame.image.load("Assets/Textures/Player/straight.png").convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.centerx = WINDOW_WIDTH//2
        self.rect.bottom = WINDOW_HEIGHT-40

        self.lives = 5
        self.velocity = 30
        self.plaser_group = plaser_group

        self.shoot_sound = pygame.mixer.Sound("Assets/Sounds/Shoot.mp3")
        self.shoot_sound.set_volume(0.5)

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.rect.x -= self.velocity
            self.image = pygame.image.load("Assets/Textures/Player/left.png").convert_alpha()
        if keys[pygame.K_RIGHT]:
            self.rect.x += self.velocity
            self.image = pygame.image.load("Assets/Textures/Player/right.png").convert_alpha()
        if keys[pygame.K_UP]:
            self.image = pygame.image.load("Assets/Textures/Player/straight.png").convert_alpha()

        if player.rect.left <= 0:
            self.rect.left = 0
        if player.rect.right >= WINDOW_WIDTH:
            self.rect.right = WINDOW_WIDTH

    def shoot(self):
        if len(self.plaser_group) < 2 + int(round_value):
            self.shoot_sound.play()
            PLaser(self.rect.centerx, self.rect.top, self.plaser_group)

    def reset(self):
        self.rect.centerx = WINDOW_WIDTH//2

class Enemy(pygame.sprite.Sprite):
    """A class to control the enemys"""
    
    def __init__(self, x, y, velocity, elaser_group):
        super().__init__()
        self.image = pygame.image.load("Assets/Textures/Enemy/enemy1.png").convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

        self.first_x = x
        self.first_y = y
        self.direction = 1
        self.velocity = 10
        self.elaser_group = elaser_group

        self.shoot_sound = pygame.mixer.Sound("Assets/Sounds/Shoot.mp3")
        self.shoot_sound.set_volume(0.2)

    def update(self):
        self.rect.x += self.direction*self.velocity

        if random.randint(0,1000) > 995 and len(elaser_group) < 3:
            self.shoot_sound.play()
            self.shoot()

    def shoot(self):
        ELaser(self.rect.centerx, self.rect.bottom, self.elaser_group)

    def reset(self):
        self.rect.topleft = (self.first_x, self.first_y)
        self.direction = 1

class PLaser(pygame.sprite.Sprite):
    """A class for player's lasers"""

    def __init__(self, x, y, plaser_group):
        super().__init__()
        self.image = pygame.image.load("Assets/Textures/Laser/plaser.png").convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y

        self.velocity = 30
        plaser_group.add(self)

    def update(self):
        self.rect.y -= self.velocity
        
        if self.rect.bottom < 0:
            self.kill()

class ELaser(pygame.sprite.Sprite):
    """A class for enemy's laser"""

    def __init__(self, x, y, elaser_group):
        super().__init__()
        self.image = pygame.image.load("Assets/Textures/laser/elaser.png").convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y

        self.velocity = 30
        elaser_group.add(self)

    def update(self):
        self.rect.y += self.velocity

        if self.rect.top > WINDOW_HEIGHT:
            self.kill()

#Lasers groups
plaser_group = pygame.sprite.Group()
elaser_group = pygame.sprite.Group()

#Player group
player_group = pygame.sprite.Group()
player = Player(plaser_group)
player_group.add(player)

#Enemy group
enemy_group = pygame.sprite.Group()

#Game object
game = Game(player, enemy_group, plaser_group, elaser_group)
game.new_round()

#The main game loop
running = True
while running:
    #Check to see if the user wants to quit
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        #Shoot
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                player.shoot()

    #Blit the background
    screen.blit(pygame.image.load("Assets/Textures/space.png"), (0,0))

    #Update display & sprite groups
    player_group.update()
    player_group.draw(screen)
    enemy_group.update()
    enemy_group.draw(screen)

    plaser_group.update()
    plaser_group.draw(screen)
    elaser_group.update()
    elaser_group.draw(screen)

    #Update & draw game objects
    game.update()
    game.draw()

    #Update the display & tick clock
    pygame.display.update()
    clock.tick(FPS)

#End the game
pygame.quit()
