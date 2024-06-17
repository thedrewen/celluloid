import pygame as pg
from Utils import Color
import pickle

class Interface:
    def __init__(self, game, image_path = None, position : tuple = (0,0), scale : tuple = None) -> None:
        
        if image_path != None:
            self.image = pg.transform.scale(pg.image.load(image_path), scale)
        self.rect = None
        self.position = position
        self.game = game
        self.rect = pg.display.get_surface().blit(self.image, self.position)
        
        self.is_active = False
        self.is_visible = True

    def event(self, event):

        self.is_active = self.rect.collidepoint(pg.mouse.get_pos())

    def draw(self):

        self.rect = pg.display.get_surface().blit(self.image, self.position)

class PauseButton():
    def __init__(self, game) -> None:
        self.screen = pg.display.get_surface()
        self.game = game

        self.pauseImage = pg.transform.scale(pg.image.load("./assets/Pause.png"), (40, 40))
        self.playImage = pg.transform.scale(pg.image.load("./assets/Play.png"), (40, 40))

        self.width = 40
        self.image = pg.Surface((self.width, 40), pg.SRCALPHA)
        self.image = self.image.convert_alpha()
        self.image.set_colorkey((0, 0, 0))
        self.rect = self.image.get_rect(center=(self.screen.get_width() // 2, 40))
        self.is_active = False
        self.is_visible = True

    def event(self, event):
        self.is_active = self.rect.collidepoint(pg.mouse.get_pos())
        if self.is_active and event.type == pg.MOUSEBUTTONDOWN:

            menu_not_open = False

            for int in self.game.interfaces:
                if isinstance(int, Menu):
                    if int.is_visible:
                        menu_not_open = True

            if event.button == 1 and not menu_not_open:
                self.game.play = not self.game.play
            elif event.button == 1:
                for int in self.game.interfaces:
                    if isinstance(int, Menu):
                        int.is_visible = False
                self.game.play = not self.game.play

        if event.type == pg.KEYDOWN:
            menu_not_open = False

            for int in self.game.interfaces:
                if isinstance(int, Menu):
                    if int.is_visible:
                        menu_not_open = True
            if event.key == pg.K_SPACE and not menu_not_open:
                self.game.play = not self.game.play


    
    def draw(self):

        self.image.fill((0, 0, 0))

        if self.is_active:
            self.image.fill(Color.WHITEOPAQUE)

        if self.game.play:
            self.image.blit(self.pauseImage, (0, 0))
        else:
            self.image.blit(self.playImage, (0, 0))

        self.rect = self.image.get_rect(center=(self.screen.get_width() // 2, 40))
        pg.display.get_surface().blit(self.image, self.rect)        

class CloseButton(Interface):

    def __init__(self, game) -> None:
        self.screen = pg.display.get_surface()
        super().__init__(image_path="assets/close.png", position=(self.screen.get_width() - 64, 0), game=game, scale=(64, 64))

        
    def event(self, event):
        
        if event.type == pg.MOUSEBUTTONDOWN:
            if event.button == 1 and self.rect.collidepoint(pg.mouse.get_pos()):
                self.game.running = False

    def draw(self):
        if self.rect.collidepoint(pg.mouse.get_pos()):
            s = pg.Surface((64, 64), pg.SRCALPHA)
            s.fill(Color.REDOPAQUE)
            self.screen.blit(s, self.rect)
        return super().draw()
    
class Statistiques(Interface):
    def __init__(self, game) -> None:

        self.image = pg.Surface((400, pg.display.get_window_size()[1]))
        self.rect = self.image.fill(Color.BLACKGREY)

        self.symbole = pg.image.load("./assets/stats.png")

        super().__init__(game=game, position=(-350, 0))

    def CreateText(self, texte : str, texte_size : int, top : int, right : bool = False, bottom : bool = False):
        font = pg.font.Font("./assets/ubuntu.ttf", texte_size)

        texte_ = font.render(texte, True, Color.WHITE)
        texte_rect = texte_.get_rect()

        if right:
            texte_rect.right = self.image.get_width() - 70
        else:
            texte_rect.left = 20

        if bottom:
            texte_rect.bottom = self.image.get_height() - top
        else:
            texte_rect.top = top
        self.drawText(texte_, texte_rect) 
        return texte_, texte_rect

    def drawText(self, font : pg.Surface, rect : pg.Rect):

        self.image.blit(font, rect)

    def addTexts(self):

        textes = [
            "Nombre de cellules :",
            str(len(self.game.entities)),
            "Nombre de morts :",
            str(self.game.deads),
            "Nombre de naissances :",
            str(self.game.borns),
            "Nombre d'anomalies :",
            str(self.game.anomalies),
            "-----",
            "-----"
        ]
        top = 20
        text_Title, text_Title_rect = self.CreateText("Statistiques", 50, top)
        top += text_Title.get_height() + 20
        right = False
        for texte in textes:
            count_cellules, count_cellules_title_rect = self.CreateText(texte, 20, top, right)
            if right:
                count_cellules_ = count_cellules
                top += 20 + count_cellules_.get_height()
            right = not right

        self.CreateText("Temps :", 20, 20, False, True)


        seconds = self.game.time
        minutes = seconds // 60
        seconds -= 60 * minutes
        hours = minutes // 60
        minutes -= 60 * hours
        
        if len(str(seconds)) == 1:
            seconds = "0"+str(seconds)
        if len(str(minutes)) == 1:
            minutes = "0"+str(minutes)
        if len(str(hours)) == 1:
            hours = "0"+str(hours)
        self.CreateText(f"{hours}:{minutes}:{seconds}", 20, 20, True, True)

    def draw(self):

        self.image.fill(Color.BLACKGREY)

        self.addTexts()

        rectRight = pg.Surface((50, pg.display.get_surface().get_height()))
        rectRight.fill(Color.BLACKGREYUP)
        symb = pg.transform.scale(self.symbole, (40, 40))
        rectRight.blit(symb, (rectRight.get_width() // 2 - symb.get_width() // 2, 10))
        self.image.blit(rectRight, (self.image.get_width() - rectRight.get_width(), 0))

        speed = 100

        isNotMenuOpen = False
        for inter in self.game.interfaces:
            if isinstance(inter, Menu):
                if inter.is_visible:
                    isNotMenuOpen = True

        if self.is_active and self.position[0] < 0 and not isNotMenuOpen:
            x = self.position[0]
            x += speed
            self.position = (x, self.position[1])
        elif not self.is_active and self.position[0] > -350:
            x = self.position[0]
            x -= speed
            self.position = (x, self.position[1])

        
        if self.position[0] > 0:
            self.position = (0, self.position[1])
        if self.position[0] < -350:
            self.position = (-350, self.position[1])


        self.rect = pg.display.get_surface().blit(self.image, self.position)

class MenuPage:
    menu = 0
class Menu(Interface):

    def __init__(self, game) -> None:
        self.screen = pg.display.get_surface()
        self.image = pg.Surface((self.screen.get_width() - 900, self.screen.get_height() - 300), pg.SRCALPHA)
        self.rect = self.image.get_rect()
        self.image = self.image.convert_alpha()
        self.is_visible = False
        self.page = MenuPage.menu

        size = 30
        self.buttons_menu = [self.CreateText("Reprendre", size), self.CreateText("Sauvegarder", size), self.CreateText("Charger", size), self.CreateText("Quitter", size)]
        
    def event(self, event):
        
        return super().event(event)


    
    def CreateText(self, texte : str, texte_size : int):
        font = pg.font.Font("./assets/ubuntu.ttf", texte_size)

        texte_ = font.render(texte, True, Color.WHITE)
        texte_rect = texte_.get_rect()
        return texte_, texte_rect
    
    def draw_menu(self):

        top = self.image.get_height() // (len(self.buttons_menu) + 1)

        rects = [None, None, None, None]

        i = 1
        for btn in self.buttons_menu:
            text, rect = btn
            
            rectSouris = pg.Rect(pg.mouse.get_pos()[0], pg.mouse.get_pos()[1], 10, 10)
            pg.draw.rect(self.screen, Color.RED, rectSouris)
            index = self.buttons_menu.index(btn)

            surface = pg.Surface((self.image.get_width() - 200, text.get_height()), pg.SRCALPHA)
            if(rects[index] != None):
                if rects[index].colliderect(rectSouris):
                    surface.fill(Color.WHITEOPAQUE)

            surface_rect = surface.get_rect(center=(self.image.get_width() // 2, top * i))
            rect.center = (surface.get_width() // 2, surface.get_height() // 2)
            surface.blit(text, rect)
            rects[index] = self.image.blit(surface, surface_rect)
            print(rects[index].colliderect(rectSouris))

            i+=1

    def draw(self):

        if self.is_visible:
            rect = pg.Rect(0, 0, self.image.get_width(), self.image.get_height())
            pg.draw.rect(self.image, Color.BLACKGREY, rect, border_radius=20)
            self.rect = self.image.get_rect()
            self.rect.center = (self.screen.get_width() // 2, self.screen.get_height() // 2)

            if self.page == MenuPage.menu:
                self.draw_menu()

            self.screen.blit(self.image, self.rect)

class MenuButton():
    def __init__(self, game) -> None:
        self.screen = pg.display.get_surface()
        self.game = game

        self.keyImage = pg.transform.scale(pg.image.load("./assets/keyboard.png"), (40, 40))

        self.width = 40
        self.image = pg.Surface((self.width, 40), pg.SRCALPHA)
        self.image = self.image.convert_alpha()
        self.image.set_colorkey((0, 0, 0))
        self.rect = self.image.get_rect(center=(self.screen.get_width() // 2, 40))
        self.is_active = False

        self.is_visible = True

    def event(self, event):
        self.is_active = self.rect.collidepoint(pg.mouse.get_pos())

        if (event.type == pg.MOUSEBUTTONDOWN and event.button == 1 and self.is_active) or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE):
            for interface in self.game.interfaces:
                if type(interface) == Menu:

                    interface.is_visible = not interface.is_visible

                    self.game.play = not interface.is_visible
    
    def draw(self):

        self.image.fill((0, 0, 0))
        if self.is_active:
            self.image.fill(Color.WHITEOPAQUE)

        self.image.blit(self.keyImage, (0, 0))

        self.rect = self.image.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() - 40))
        pg.display.get_surface().blit(self.image, self.rect)