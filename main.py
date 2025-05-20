import pygame as pg
from pygame import gfxdraw
import time, random, os, math, threading
from Utils import Color, taille_cote_carrer_inscrit
from Interfaces import CloseButton, Statistiques, PauseButton, Menu, MenuButton

pg.init()

CELLULE_DEFAULT_COLOR = Color.RED
CELLULE_DEFAULT_LUCK_GENETIC_ERROR = (0, 10)
CELLULE_DEFAULT_LUCK_OBTAINING_CELL_COLOR = 5
CELLULE_DEFAULT_RADIUS = (10, 50)
CELLULE_DEFAULT_FOOD = 25
CELLULE_DEFAULT_SPEED_DIVISER = 10
CELLULE_DEFAULT_SECOND_FOOD_LOST = 3
CELLULE_DEFAULT_SECOND_REPLICATION = 3
CELLULE_DEFAULT_FOOD_LOST = (1, 10)
CELLULE_DEFAULT_MAX_RADIUS = 130
CELLULE_DEFAULT_SPAWN_RADIUS = 100

class Entity:
    def __init__(self, game, position : tuple[int, int] = None, color : tuple[int, int, int] = CELLULE_DEFAULT_COLOR, luck_genetic_error : int = -1, test : bool = False, is_pochet : bool = False) -> None:
        screen = pg.display.get_surface()
        self.game = game
        self.is_pochet = is_pochet
        self.image = None
        if self.is_pochet:
            self.image = pg.image.load("./assets/pochet.png")
        
        if luck_genetic_error == -1:
            luck_genetic_error = random.randint(CELLULE_DEFAULT_LUCK_GENETIC_ERROR[0], CELLULE_DEFAULT_LUCK_GENETIC_ERROR[1])
        if position == None:
            self.position = (random.randint(15, screen.get_width() - 15), random.randint(15, screen.get_height() - 15))
        else:
            self.position = position
        self.color = color
        self.dead = False
        self.radius = random.randint(CELLULE_DEFAULT_RADIUS[0], CELLULE_DEFAULT_RADIUS[1])
        self.new_radius = self.radius
        self.luck_genetic_error = luck_genetic_error

        self.food = CELLULE_DEFAULT_FOOD

        self.secondFood = 0
        self.secondReproduction = 0
        self.lapse_seconde = time.time()

        self.test = test

        self.new_position = self.generate_position()
        self.speed = (CELLULE_DEFAULT_MAX_RADIUS - self.radius) // 10

    def generate_position(self):
        screen = pg.display.get_surface()
        return (random.randint(0, screen.get_width()), random.randint(0, screen.get_height()))

    def move(self):
        screen = pg.display.get_surface()
        x, y = self.position
        self.speed = (CELLULE_DEFAULT_MAX_RADIUS - self.radius) // 10
        new_x, new_y = self.new_position
        rect_y = pg.Rect(0, new_y, screen.get_width(), 1)
        rect_x = pg.Rect(new_x, 0, 1, screen.get_height())
        rect_detect = pg.Rect(new_x - self.speed, new_y - self.speed, self.speed * 2, self.speed * 2)
        
        if self.game.devmode:
            pg.draw.rect(screen, Color.RED, rect_detect)
            pg.draw.rect(screen, Color.GREEN, rect_y)
            pg.draw.rect(screen, Color.GREEN, rect_x)

        if not rect_detect.colliderect(self.rect):
            if x < new_x and not self.rect.colliderect(rect_x):
                x += self.speed
            elif not self.rect.colliderect(rect_x):
                x -= self.speed 
    
            if y < new_y and not self.rect.colliderect(rect_y):
                y += self.speed
            elif not self.rect.colliderect(rect_y):
                y -= self.speed 
        else:
            self.new_position = self.generate_position()

        self.position = (x, y)
            
            

    def collision(self, entities : list):

        for entity in entities:
            if entity != self:
                try:
                    if self.rect.colliderect(entity.rect):
                        if self.radius > entity.radius:
                            entity.dead = True
                            self.new_radius = self.radius + entity.radius // 10
                            if self.new_radius > CELLULE_DEFAULT_MAX_RADIUS:
                                self.new_radius = CELLULE_DEFAULT_MAX_RADIUS
                            if random.randint(1, 100) >= 100 - CELLULE_DEFAULT_LUCK_OBTAINING_CELL_COLOR:
                                self.color = entity.color
                        elif self.radius < entity.radius:
                            self.dead = True
                            entity.new_radius = entity.radius + self.radius // 10
                            if entity.new_radius > CELLULE_DEFAULT_MAX_RADIUS:
                                entity.new_radius = CELLULE_DEFAULT_MAX_RADIUS
                            if random.randint(1, 100) >= 100 - CELLULE_DEFAULT_LUCK_OBTAINING_CELL_COLOR:
                                entity.color = self.color
                        else:
                            entity.dead = True
                            self.dead = True
                            

                except Exception as e:
                    pass
        if self.position[0] > pg.display.get_window_size()[0] or self.position[1] > pg.display.get_window_size()[1] or self.position[0] < 0 or self.position[1] < 0:
            self.dead = True
            

    def update(self, entities : list):

        screen = pg.display.get_surface()
        options = {"anomalies" : 0}
        if not self.dead:

            if self.radius > self.new_radius:
                self.radius -= 1 

                if self.radius < self.new_radius:
                    self.radius = self.new_radius
                
            if self.radius < self.new_radius:
                self.radius += 1 

                if self.radius > self.new_radius:
                    self.radius = self.new_radius

            if time.time() - self.lapse_seconde >= 1:
                self.lapse_seconde = time.time()
                self.secondFood += 1
                self.secondReproduction += 1
                
            if self.secondFood == CELLULE_DEFAULT_SECOND_FOOD_LOST:
                self.secondFood = 0
                self.food -= random.randint(CELLULE_DEFAULT_FOOD_LOST[0], CELLULE_DEFAULT_FOOD_LOST[1])

            if self.food <= 0:
                self.food = CELLULE_DEFAULT_FOOD
                self.new_radius -= self.radius // 3

            if self.radius <= 0:
                
                self.dead = True
            elif self.radius > CELLULE_DEFAULT_MAX_RADIUS:
                self.radius = CELLULE_DEFAULT_MAX_RADIUS

            if self.secondReproduction >= CELLULE_DEFAULT_SECOND_REPLICATION:
                self.secondReproduction = 0

                if random.randint(0, 100) <= 100 - self.luck_genetic_error:
                    entity =  Entity(self.game, screen, color=self.color, is_pochet=self.is_pochet)
                else:
                    options["anomalies"] += 1
                    if random.randint(0, 100) >= 90:
                        entity =  Entity(self.game, screen, color=self.color, is_pochet=True)
                    else:   
                        entity = Entity(self.game, screen, color=Color.random(), is_pochet=self.is_pochet)

                new_position = (self.position[0] + random.randint(-CELLULE_DEFAULT_SPAWN_RADIUS - self.radius - entity.radius, CELLULE_DEFAULT_SPAWN_RADIUS + self.radius + entity.radius), self.position[1] + random.randint(-CELLULE_DEFAULT_SPAWN_RADIUS - self.radius - entity.radius, CELLULE_DEFAULT_SPAWN_RADIUS + self.radius + entity.radius))
                while pg.rect.Rect(new_position[0], new_position[1], 1, 1).colliderect(self.rect):
                    new_position = (self.position[0] + random.randint(-CELLULE_DEFAULT_SPAWN_RADIUS - self.radius - entity.radius, CELLULE_DEFAULT_SPAWN_RADIUS + self.radius + entity.radius), self.position[1] + random.randint(-CELLULE_DEFAULT_SPAWN_RADIUS - self.radius - entity.radius, CELLULE_DEFAULT_SPAWN_RADIUS + self.radius + entity.radius))

                entity.position = new_position
                
                options["new_cellule"] = entity
            self.move()
            self.collision(entities)
            
        return options


    def draw(self):
        screen = pg.display.get_surface()
        if not self.dead:
            self.surface = pg.Surface((taille_cote_carrer_inscrit(self.radius), taille_cote_carrer_inscrit(self.radius)), pg.SRCALPHA, 32)
            self.surface.convert_alpha()
            pg.draw.circle(screen, self.color, self.position, self.radius)
            pg.draw.circle(screen, Color.addOneToColor(self.color), self.position, self.radius - self.radius // 3)

            font = pg.font.Font("./assets/ubuntu.ttf", self.radius // 3)

            texte = font.render("R = "+str(self.radius), True, Color.WHITE)
            texte_rect = texte.get_rect()
            texte_rect.top = self.position[1] - texte.get_height() // 2 - texte.get_height() // 2 
            texte_rect.left = self.position[0] - texte.get_width() // 2

            texte1 = font.render("Food = "+str(self.food), True, Color.WHITE)
            texte_rect1 = texte.get_rect()
            texte_rect1.top = self.position[1] - texte1.get_height() // 2 + texte1.get_height() // 2
            texte_rect1.left = self.position[0] - texte1.get_width() // 2
            
            if self.game.devmode:
                screen.blit(texte, texte_rect)
                screen.blit(texte1, texte_rect1)

            if self.image != None: 
                rect = self.image.get_rect(center=self.position)
                self.surface.blit(pg.transform.scale(self.image, (self.radius * 2, self.radius * 2)), rect)
            
            self.rect = self.surface.get_rect(center=self.position)
            screen.blit(self.surface, self.rect)
        


class Game:
    def __init__(self) -> None:
        
        self.screen = pg.display.set_mode((1600, 900), pg.NOFRAME)
        pg.display.set_icon(pg.image.load("./assets/logo.ico"))
        self.background = pg.image.load("./assets/background.png")

        self.clock = pg.time.Clock()
        pg.display.set_caption("Celluloid")
        self.running = True

        self.musics = os.listdir("musics")
        self.music_index = 0

        self.entities = []
        self.interfaces = [PauseButton(self), Statistiques(self), CloseButton(self)] # Menu(self) MenuButton(self)

        # statistique
        self.deads = 0
        self.borns = 0
        self.anomalies = 0

        self.time = 0

        self.play = True
        self.devmode = False

    def runRPC(self):
        actual_rpc_anom = self.anomalies
        while self.running:
            if actual_rpc_anom != self.anomalies:
                self.rpc.set_activity(
                    state="Celluloid ZeroPlayerGame",
                    details="Anomalies : " + str(self.anomalies),
                    large_image="logo"
                )
                actual_rpc_anom = self.anomalies
            time.sleep(1)
            

        self.rpc.disconnect()


    def interface(self):
        for interface in self.interfaces:
            interface.draw()

    def eventManager(self):
        global CELLULE_DEFAULT_COLOR, CELLULE_DEFAULT_LUCK_GENETIC_ERROR, CELLULE_DEFAULT_LUCK_OBTAINING_CELL_COLOR, CELLULE_DEFAULT_RADIUS, CELLULE_DEFAULT_FOOD, CELLULE_DEFAULT_SPEED_DIVISER, CELLULE_DEFAULT_SECOND_REPLICATION, CELLULE_DEFAULT_FOOD_LOST, CELLULE_DEFAULT_MAX_RADIUS, CELLULE_DEFAULT_SPAWN_RADIUS
        for event in pg.event.get():
            if event.type == pg.MOUSEWHEEL:
                # print(event.x, event.y)
                pass
            for interface in self.interfaces:
                interface.event(event)
            if event.type == pg.QUIT:
                self.running = False
            elif event.type == self.MUSIC_END:
                pg.mixer.music.load("musics/"+self.musics[self.music_index])
                self.music_index+=1
                if len(self.musics) == self.music_index:
                    self.music_index = 0
                pg.mixer.music.play()
            elif event.type == pg.MOUSEBUTTONDOWN:

                is_not_interface = True
                for interface in self.interfaces:
                    if interface.is_active and interface.is_visible:
                        is_not_interface = False

                if is_not_interface:
                    if event.button == 1:
                        self.entities.append(Entity(self, pg.mouse.get_pos()))
                    if event.button == 3:
                        for entity in self.entities:
                            if entity.rect.collidepoint(pg.mouse.get_pos()[0], pg.mouse.get_pos()[1]):
                                entity.dead = True
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_F3:
                    self.devmode = not self.devmode
                if event.key == pg.K_v:
                    pass
        

    def run(self):

        pg.mixer.init()
        pg.mixer.music.load("musics/"+self.musics[self.music_index])
        self.music_index+=1
        if len(self.musics) == self.music_index:
            self.music_index = 0
        pg.mixer.music.play()

        self.MUSIC_END = pg.USEREVENT+1
        pg.mixer.music.set_endevent(self.MUSIC_END)

        
        while self.running:

            pg.display.flip()

            self.screen.fill(Color.WHITE)
            self.screen.blit(self.background, (0, 0))

            if self.devmode:
                font = pg.font.Font("./assets/ubuntu.ttf", 20)

                texte = font.render("DevModeEnable (F3)", True, Color.WHITE)
                texte_rect = texte.get_rect()
                texte_rect.bottomright = (self.screen.get_width(), self.screen.get_height())
                
                self.screen.blit(texte, texte_rect)

            entities = self.entities
            self.entities = []
            for i in range(0, CELLULE_DEFAULT_MAX_RADIUS + 1):
                for entity in entities:
                    if entity.radius == i or (entity.radius > CELLULE_DEFAULT_MAX_RADIUS and i == CELLULE_DEFAULT_MAX_RADIUS):
                        self.entities.append(entity)

            self.eventManager()

            dead_entities = []
            new_entities = []
            for entity in self.entities:
                if entity.dead:
                    dead_entities.append(entity)
                else:
                    entity.draw()
                    if self.play:
                        options = entity.update(self.entities)
                        self.anomalies += options["anomalies"]
                        if "new_cellule" in options:
                            new_entities.append(options["new_cellule"])


            if self.play:
                for entity in dead_entities:
                    self.entities.remove(entity)
                    self.deads += 1
                for entity in new_entities:
                    self.entities.append(entity)
                    self.borns += 1

            self.interface()
            self.time = pg.time.get_ticks() // 1000
            self.clock.tick(60)

Game().run()





        

    