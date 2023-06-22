import math
import random
import pygame


# Inicializace hry
pygame.init()

width = 1000
height = 1000
window = pygame.display.set_mode((width, height))

# Obrázky a pozadí
bg = pygame.image.load("img/bg_star.jpg")
alienImg = pygame.image.load("img/alien.png")
playerRocket = pygame.image.load("img/rocket.png")
star = pygame.image.load("img/star.png")
asteroid_small = pygame.image.load("img/asteroid_small.png")
asteroid_medium = pygame.image.load("img/asteroid_medium.png")
asteroid_big = pygame.image.load("img/asteroid_big.png")

# Načtení a nastavení zvuků
shoot_sound = pygame.mixer.Sound("sounds/laserShoot.wav")
explosion_sound = pygame.mixer.Sound("sounds/explosion.wav")
powerUp_sound = pygame.mixer.Sound("sounds/powerUp.wav")
bad_explosion_sound = pygame.mixer.Sound("sounds/bad_explosion.wav")
alienLaserShoot_sound = pygame.mixer.Sound("sounds/alienLaserShoot.wav")
shoot_sound.set_volume(.25)
explosion_sound.set_volume(.25)
bad_explosion_sound.set_volume(.4)
alienLaserShoot_sound.set_volume(.25)

# Nastavení nadpisu hry
pygame.display.set_caption("Asteroids")


# Nastavení hry
clock = pygame.time.Clock()
fps = 60

gameover = False
lives = 3
score = 0
rapidFire = False
rfStart = -1
isSoundOn = True
highScore = 0



class Player(object):
    # Třída podle které vytvoříme raketu, kterou ovládáme
    def __init__(self):
        self.img = playerRocket
        self.w = self.img.get_width()
        self.h = self.img.get_height()
        self.x = width//2
        self.y = height//2
        self.angle = 0
        self.rotatedSurf = pygame.transform.rotate(self.img, self.angle)
        self.rotatedRect = self.rotatedSurf.get_rect()
        self.rotatedRect.center = (self.x, self.y)
        self.cosine = math.cos(math.radians(self.angle + 90))
        self.sine = math.sin(math.radians(self.angle + 90))
        self.head = (self.x + self.cosine * self.w//2, self.y - self.sine * self.h//2)

    # Vykreslení rakety
    def draw(self, window):
        window.blit(self.rotatedSurf, self.rotatedRect)

    # Otáčení vlevo
    def turnLeft(self):
        self.angle += 5
        self.rotatedSurf = pygame.transform.rotate(self.img, self.angle)
        self.rotatedRect = self.rotatedSurf.get_rect()
        self.rotatedRect.center = (self.x, self.y)
        self.cosine = math.cos(math.radians(self.angle + 90))
        self.sine = math.sin(math.radians(self.angle + 90))
        self.head = (self.x + self.cosine * self.w//2, self.y - self.sine * self.h//2)

    # Otáčení vpravo
    def turnRight(self):
        self.angle -= 5
        self.rotatedSurf = pygame.transform.rotate(self.img, self.angle)
        self.rotatedRect = self.rotatedSurf.get_rect()
        self.rotatedRect.center = (self.x, self.y)
        self.cosine = math.cos(math.radians(self.angle + 90))
        self.sine = math.sin(math.radians(self.angle + 90))
        self.head = (self.x + self.cosine * self.w//2, self.y - self.sine * self.h//2)

    # Pohyb vpřed
    def moveForward(self):
        self.x += self.cosine * 6
        self.y -= self.sine * 6
        self.rotatedSurf = pygame.transform.rotate(self.img, self.angle)
        self.rotatedRect = self.rotatedSurf.get_rect()
        self.rotatedRect.center = (self.x, self.y)
        self.cosine = math.cos(math.radians(self.angle + 90))
        self.sine = math.sin(math.radians(self.angle + 90))
        self.head = (self.x + self.cosine * self.w // 2, self.y - self.sine * self.h // 2)

    # Pokud proletíme hranicí okna tak vyletíme z opačné hranice okna
    def updateLocation(self):
        if self.x > width + 50:
            self.x = 0
        elif self.x < -50:
            self.x = width
        elif self.y < -50:
            self.y = height
        elif self.y > height + 50:
            self.y = 0

class Bullet(object):
    # Třída podle níž tvoříme střely z rakety

    # konstruktor
    def __init__(self):
        self.point = player.head
        self.x, self.y = self.point
        self.w = 4
        self.h = 4
        self.c = player.cosine
        self.s = player.sine
        self.xv = self.c * 10
        self.yv = self.s * 10

    # Pohyb náboje
    def move(self):
        self.x += self.xv
        self.y -= self.yv

    # Definice vzhledu náboje
    def draw(self, window):
        pygame.draw.rect(window, (255, 255, 0), [self.x, self.y, self.w, self.h])

    # Kontrola zda se náboj stále nachází v okně
    def checkOffScreen(self):
        if self.x < -50 or self.x > width or self.y > height or self.y < -50:
            return True

class Asteroid(object):
    # Třída podle níž tvoříme objekty asteroid

    # Konstruktor
    def __init__(self, rank):
        self.rank = rank
        if self.rank == 1:
            self.image = asteroid_small
        elif self.rank == 2:
            self.image = asteroid_medium
        else:
            self.image = asteroid_big
        self.w = 50 * rank
        self.h = 50 * rank
        self.ranPoint = random.choice([(random.randrange(0, width-self.w), random.choice([-1 * self.h - 5, height + 5])), (random.choice([-1*self.w - 5, width + 5]), random.randrange(0, height - self.h))])
        self.x, self.y = self.ranPoint
        if self.x < width//2:
            self.xdir = 1
        else:
            self.xdir = -1
        if self.y < height//2:
            self.ydir = 1
        else:
            self.ydir = -1
        self.xv = self.xdir * random.randrange(1,3)
        self.yv = self.ydir * random.randrange(1,3)

    # Vykreslí asteroidy
    def draw(self, window):
        window.blit(self.image, (self.x, self.y))



class Alien(object):
    # Třída, podle které tvoří objekt vetřelce (vesmírný talíř)

    # Konstruktor
    def __init__(self):
        self.img = alienImg
        self.w = self.img.get_width()
        self.h = self.img.get_height()
        self.ranPoint = random.choice(
            [(random.randrange(0, width - self.w), random.choice([-1 * self.h - 5, height + 5])),
             (random.choice([-1 * self.w - 5, width + 5]), random.randrange(0, height - self.h))])
        self.x, self.y = self.ranPoint
        if self.x < width//2:
            self.xdir = 1
        else:
            self.xdir = -1
        if self.y < height//2:
            self.ydir = 1
        else:
            self.ydir = -1
        self.xv = self.xdir * 2
        self.yv = self.ydir * 2

    # Vykreslení vetřelce
    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

class AlienBullet(object):
    # Třída podle které tvoříme objekty nábojů vetřelce

    # Kontrola
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.w = 4
        self.h = 4
        self.dx, self.dy = player.x - self.x, player.y - self.y
        self.dist = math.hypot(self.dx, self.dy)
        self.dx, self.dy = self.dx / self.dist, self.dy / self.dist
        self.xv = self.dx * 5
        self.yv = self.dy * 5

    # Vykreslení nábojů vetřelce
    def draw(self, window):
        pygame.draw.rect(window, (255, 165, 0), [self.x, self.y, self.w, self.h])

class Star(object):
    # Třída podle které se tvoří objekt hvězda

    # Konstruktor
    def __init__(self):
        self.img = star
        self.w = self.img.get_width()
        self.h = self.img.get_height()
        self.ranPoint = random.choice(
            [(random.randrange(0, width - self.w), random.choice([-1 * self.h - 5, height + 5])),
             (random.choice([-1 * self.w - 5, width + 5]), random.randrange(0, height - self.h))])
        self.x, self.y = self.ranPoint
        if self.x < width//2:
            self.xdir = 1
        else:
            self.xdir = -1
        if self.y < height//2:
            self.ydir = 1
        else:
            self.ydir = -1
        self.xv = self.xdir * 2
        self.yv = self.ydir * 2

    # Vykreslení hvězdy
    def draw(self, window):
        window.blit(self.img, (self.x, self.y))


# Vykreslení hry
def redrawGameWindow():
    window.blit(bg, (0,0))
    font = pygame.font.SysFont("Arial", 30)
    livesText = font.render("Lives: " + str(lives), 1, (255, 255, 255))
    playAgainText = font.render("Press Tab to Play Again", 1, (255, 255, 255))
    scoreText = font.render("Score: " + str(score), 1, (255, 255, 255))
    highScoreText = font.render("High Score: " + str(highScore), 1, (255, 255, 255))

    player.draw(window)
    for one_asteroid in asteroids:
        one_asteroid.draw(window)
    for one_bullet in playerBullets:
        one_bullet.draw(window)
    for one_star in stars:
        one_star.draw(window)
    for one_alien in aliens :
        one_alien.draw(window)
    for one_bullet in aliensBullets:
        one_bullet.draw(window)

    if rapidFire:
        pygame.draw.rect(window, (0, 0, 0), [width//2 - 51, 19, 102, 22])
        pygame.draw.rect(window, (255, 255, 255), [width//2 - 50, 20, 100 - 100*(count - rfStart)/500, 20])

    if gameover:
        window.blit(playAgainText, (width//2-playAgainText.get_width()//2, height//2 - playAgainText.get_height()//2))
    window.blit(scoreText, (width - scoreText.get_width() - 25, 25))
    window.blit(livesText, (25, 25))
    window.blit(highScoreText, (width - highScoreText.get_width() - 25, 35 + scoreText.get_height()))
    pygame.display.update()

# Použití logiky
player = Player()
playerBullets = []
asteroids = []
count = 0
stars = []
aliens = []
aliensBullets = []

# Hlavní cyklus

run = True
while run:
    count += 1

    # Vykreslení a postupné updatování celé hry
    if not gameover:
        # Určení po jak dlouhých časových intervalech se objevují asteroidy, hvězda, vetřelec a jeho střely
        if count % 50 == 0:
            ran = random.choice([1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 3, 3])
            asteroids.append(Asteroid(ran))
        if count % 1000 == 0:
            stars.append(Star())
        if count % 750 == 0:
            aliens.append(Alien())
        for i, one_alien in enumerate(aliens):
            one_alien.x += one_alien.xv
            one_alien.y += one_alien.yv
            if one_alien.x > width + 150 or one_alien.x + one_alien.w < -100 or one_alien.y > height + 150 or one_alien.y + one_alien.h < -100:
                aliens.pop(i)
            if count % 60 == 0:
                aliensBullets.append(AlienBullet(one_alien.x + one_alien.w//2, one_alien.y + one_alien.h//2))
                if isSoundOn:
                    alienLaserShoot_sound.play()

            # Kontrola kolize hráče s vetřelcem
            if (one_alien.x >= player.x - player.w//2 and one_alien.x <= player.x + player.w//2) or (one_alien.x + one_alien.w <= player.x + player.w//2 and one_alien.x + one_alien.w >= player.x - player.w//2):
                if(one_alien.y >= player.y - player.h//2 and one_alien.y <= player.y + player.h//2) or (one_alien.y + one_alien.h >= player.y - player.h//2 and one_alien.y + one_alien.h <= player.y + player.h//2):
                    lives -= 1
                    aliens.pop(aliens.index(one_alien))
                    if isSoundOn:
                        bad_explosion_sound.play()
                    break

            # kontrola kolize střely hráče s vetřelcem
            for one_bullet in playerBullets:
                if (one_bullet.x >= one_alien.x and one_bullet.x <= one_alien.x + one_alien.w) or one_bullet.x + one_bullet.w >= one_alien.x and one_bullet.x + one_bullet.w <= one_alien.x + one_alien.w:
                    if (one_bullet.y >= one_alien.y and one_bullet.y <= one_alien.y + one_alien.h) or one_bullet.y + one_bullet.h >= one_alien.y and one_bullet.y + one_bullet.h <= one_alien.y + one_alien.h:
                        aliens.pop(i)
                        if isSoundOn:
                            explosion_sound.play()
                        score += 50
                        break



        # Pohyb střely vetřelce a kontrola kolize střely vetřelce s hrářem
        for i, one_bullet in enumerate(aliensBullets):
            one_bullet.x += one_bullet.xv
            one_bullet.y += one_bullet.yv
            if (one_bullet.x >= player.x - player.w//2 and one_bullet.x <= player.x + player.w//2) or one_bullet.x + one_bullet.w >= player.x - player.w//2 and one_bullet.x + one_bullet.w <= player.x + player.w//2:
                if (one_bullet.y >= player.y - player.h//2 and one_bullet.y <= player.y + player.h//2) or one_bullet.y + one_bullet.h >= player.y - player.h//2 and one_bullet.y + one_bullet.h <= player.y + player.h//2:
                    lives -= 1
                    aliensBullets.pop(i)
                    if isSoundOn:
                        bad_explosion_sound.play()
                    break

        # Pohyb střely hráče
        player.updateLocation()
        for one_bullet in playerBullets:
            one_bullet.move()
            # Kontrola zda se střela stále nachází v okně
            if one_bullet.checkOffScreen():
                playerBullets.pop(playerBullets.index(one_bullet))

        # Pohyb asteroidů
        for one_asteroid in asteroids:
            one_asteroid.x += one_asteroid.xv
            one_asteroid.y += one_asteroid.yv

            # Kontrola kolize asteroidů s hráčem
            if (one_asteroid.x >= player.x - player.w//2 and one_asteroid.x <= player.x + player.w//2) or (one_asteroid.x + one_asteroid.w <= player.x + player.w//2 and one_asteroid.x + one_asteroid.w >= player.x - player.w//2):
                if(one_asteroid.y >= player.y - player.h//2 and one_asteroid.y <= player.y + player.h//2) or (one_asteroid.y + one_asteroid.h >= player.y - player.h//2 and one_asteroid.y + one_asteroid.h <= player.y + player.h//2):
                    lives -= 1
                    asteroids.pop(asteroids.index(one_asteroid))
                    if isSoundOn:
                        bad_explosion_sound.play()
                    break

            # Kolize náboje s asteroidem
            for one_bullet in playerBullets:
                if (one_bullet.x >= one_asteroid.x and one_bullet.x <= one_asteroid.x + one_asteroid.w) or one_bullet.x >= one_asteroid.x and one_bullet.x + one_bullet.w <= one_asteroid.x + one_asteroid.w:
                    if (one_bullet.y >= one_asteroid.y and one_bullet.y <= one_asteroid.y + one_asteroid.h) or one_bullet.y + one_bullet.h >= one_asteroid.y and one_bullet.y + one_bullet.h <= one_asteroid.y + one_asteroid.h:
                        if one_asteroid.rank == 3:
                            if isSoundOn:
                                explosion_sound.play()
                            score += 10
                            na1 = Asteroid(2)
                            na2 = Asteroid(2)
                            na1.x = one_asteroid.x
                            na2.x = one_asteroid.x
                            na1.y = one_asteroid.y
                            na2.y = one_asteroid.y
                            asteroids.append(na1)
                            asteroids.append(na2)
                        elif one_asteroid.rank == 2:
                            if isSoundOn:
                                explosion_sound.play()
                            score += 20
                            na1 = Asteroid(1)
                            na2 = Asteroid(1)
                            na1.x = one_asteroid.x
                            na2.x = one_asteroid.x
                            na1.y = one_asteroid.y
                            na2.y = one_asteroid.y
                            asteroids.append(na1)
                            asteroids.append(na2)
                        else:
                            score += 30
                            if isSoundOn:
                                explosion_sound.play()
                        asteroids.pop(asteroids.index(one_asteroid))
                        playerBullets.pop(playerBullets.index(one_bullet))
                        break

        # Pohyb hvězdy
        for one_star in stars:
            one_star.x += one_star.xv
            one_star.y += one_star.yv
            if one_star.x < -100 - one_star.w or one_star.x > width + 100 or one_star.y > height + 100 or one_star.y < -100 - one_star.h:
                stars.pop(stars.index(one_star))
                break

            # Kontrola kolize hráčovy střely s hvězdou
            for one_bullet in playerBullets:
                if (one_bullet.x >= one_star.x and one_bullet.x <= one_star.x + one_star.w) or one_bullet.x + one_bullet.w >= one_star.x and one_bullet.x + one_bullet.w <= one_star.x + one_star.w:
                    if (one_bullet.y >= one_star.y and one_bullet.y <= one_star.y + one_star.h) or one_bullet.y + one_bullet.h >= one_star.y and one_bullet.y + one_bullet.h <= one_star.y + one_star.h:
                        rapidFire = True
                        rfStart = count
                        if isSoundOn:
                            powerUp_sound.play()
                        stars.pop(stars.index(one_star))
                        playerBullets.pop(playerBullets.index(one_bullet))
                        break

        # Kontrola počtu životů
        if lives <= 0:
            gameover = True


        if rfStart != -1:
            if count - rfStart > 500:
                rapidFire = False
                rfStart = -1

        # Pohyb hráče pomocí šipek na klávesnici a kláves W, S, A, D
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            player.turnLeft()
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            player.turnRight()
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            player.moveForward()
        if keys[pygame.K_SPACE]:
            if rapidFire:
                playerBullets.append(Bullet())
                if isSoundOn:
                    shoot_sound.play()

    for event in pygame.event.get():
        # Ukončení hry po stisknutí křížku v pravém horním rohu okna
        if event.type == pygame.QUIT:
            run = False
        # Vypuštění střely hráčem pomocí klávesy mezerník
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if not gameover:
                    if not rapidFire:
                        playerBullets.append(Bullet())
                        if isSoundOn:
                            shoot_sound.play()

            # Vypnutí a zapnutí zvuku u hry pomocí klávesy M
            if event.key == pygame.K_m:
                isSoundOn = not isSoundOn

            # Po konci hry můžeme znovu začít hrát pomocí klávesy Tab
            if event.key == pygame.K_TAB:
                if gameover:
                    gameover = False
                    lives = 3
                    asteroids.clear()
                    aliens.clear()
                    aliensBullets.clear()
                    stars.clear()
                    if score > highScore:
                        highScore = score
                    score = 0

    # Vložení pozadí
    redrawGameWindow()

    # Updatování hry
    pygame.display.update()

    # Zpomalen cyklu
    clock.tick(fps)

pygame.quit()