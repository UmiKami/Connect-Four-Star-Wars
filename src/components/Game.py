import requests
import cv2
import pygame
import os
import glob

os.environ['SDL_AUDIODRIVER'] = 'dummy'  # Use dummy audio driver

class Game:
    def __init__(self):
        # Initialize Pygame
        print("Initializing Pygame...")
        pygame.init()
        
        # Set up the display
        self.width = 800
        self.height = 600
        self.screen = pygame.display.set_mode((self.width, self.height))
        print("Display set up.")

        # Load the font with increased size for victory message
        self.font = pygame.font.Font("/workspaces/Connect-Four-Star-Wars/assets/fonts/Starjedi.ttf", 48)  
        
        # Load the icons
        self.empire_icon = pygame.image.load("/workspaces/Connect-Four-Star-Wars/assets/font-awesome/icons/empire-icon.png").convert_alpha()
        self.rebel_icon = pygame.image.load("/workspaces/Connect-Four-Star-Wars/assets/font-awesome/icons/rebel-icon.png").convert_alpha()
        print("Icons loaded.")

        # Set the caption
        pygame.display.set_caption("Star Wars Connect 4")
        
        # Initialize the clock
        self.clock = pygame.time.Clock()
        
        # Initialize the custom board
        self.custom_board = CustomBoard(self)
        print("Custom board initialized.")
        
        # Initialize the running flag
        self.running = True

        # Initialize the game over flag
        self.game_over = False
                
        # Initialize the mixer and load sounds
        pygame.mixer.init()
        self.background_music = pygame.mixer.Sound("/workspaces/Connect-Four-Star-Wars/assets/sounds/space_battle_music.mp3")
        self.background_music.set_volume(1)
        self.background_music.play(-1)
        print("Background music loaded and playing.")

        # Load wallpaper images
        self.wallpapers = self.load_wallpapers("/workspaces/Connect-Four-Star-Wars/assets/animations/*.jpg")
        self.current_wallpaper_index = 0
        self.wallpaper_change_time = 4000  
        self.last_wallpaper_change = pygame.time.get_ticks()  
        print(f"Loaded {len(self.wallpapers)} wallpapers.")

        # Set button properties
        self.button_color = (50, 50, 50)
        self.button_hover_color = (70, 70, 70)
        self.button_width = 120  
        self.button_height = 40  
        self.button_rect = pygame.Rect((self.width // 2 - self.button_width // 2, self.height - self.button_height - 20), (self.button_width, self.button_height))

    def load_wallpapers(self, pattern):
        images = []
        for filepath in glob.glob(pattern):
            image = pygame.image.load(filepath).convert()
            images.append(pygame.transform.scale(image, (self.width, self.height)))  
        return images

    def run(self):
        print("Starting the game loop...")
        while self.running:
            self.handle_events()
            self.draw_background() 
            self.custom_board.draw()  
            self.draw_restart_button()  
            pygame.display.flip()  

    def draw_background(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_wallpaper_change > self.wallpaper_change_time:
            self.current_wallpaper_index = (self.current_wallpaper_index + 1) % len(self.wallpapers)
            self.last_wallpaper_change = current_time

        self.screen.blit(self.wallpapers[self.current_wallpaper_index], (0, 0))  

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  
                    if self.game_over:  
                        self.restart_game()  
                    elif self.button_rect.collidepoint(event.pos):
                        self.restart_game()  
                    else:
                        column = (event.pos[0] - (self.width - (self.custom_board.columns * self.custom_board.cell_size)) // 2) // self.custom_board.cell_size
                        self.custom_board.drop_piece(column)  
                        requests.post('http://localhost:3002/move', json={'action': f'drop_piece,{column}'})  # Enviar acción al servidor Flask

    def draw_restart_button(self):
        mouse_pos = pygame.mouse.get_pos()
        if self.button_rect.collidepoint(mouse_pos):
            color = self.button_hover_color
        else:
            color = self.button_color

        pygame.draw.rect(self.screen, color, self.button_rect)

        font = pygame.font.Font(None, 36)  
        text_surface = font.render("Restart", True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=self.button_rect.center)
        self.screen.blit(text_surface, text_rect)

    def show_victory(self, winner):
        self.game_over = True  
        icon = self.empire_icon if winner == 'Imperial' else self.rebel_icon
        
        original_width, original_height = icon.get_size()
        new_height = self.height // 2
        aspect_ratio = original_width / original_height
        new_width = int(new_height * aspect_ratio)
        icon = pygame.transform.scale(icon, (new_width, new_height))

        icon_rect = icon.get_rect(center=(self.width // 2, self.height // 4))  
        self.screen.blit(icon, icon_rect)

        victory_text = f"{winner} Wins!"
        text_color = (255, 0, 0) if winner == 'Imperial' else (0, 0, 255)  
        victory_surface = self.font.render(victory_text, True, text_color)
        text_rect = victory_surface.get_rect(center=(self.width // 2, self.height // 2 + icon_rect.height // 2))
        self.screen.blit(victory_surface, text_rect)  

        pygame.display.flip()
        pygame.time.wait(3000)  

    def restart_game(self):
        self.custom_board = CustomBoard(self)  
        self.game_over = False  

    def process_action(self, action):
        if action.startswith("drop_piece"):
            _, column = action.split(",")
            self.custom_board.drop_piece(int(column))  # Asegúrate de que drop_piece esté implementado en CustomBoard
