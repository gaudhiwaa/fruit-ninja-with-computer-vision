import pygame
from constants import screen_height, screen_width, screen, white, black, clock

class MainMenu:
    def __init__(self):
        self.show_start_text = True
        self.start_font = pygame.font.Font(None, 36)
        self.start_text = self.start_font.render("Start Game", True, white)
        self.subtitle_font = pygame.font.Font(None, 24)
        self.subtitle_text = self.subtitle_font.render(
            "Ensure good lighting—neither too dark nor too bright.", True, white)
        self.subtitle_font_2 = pygame.font.Font(None, 24)
        self.subtitle_text_2 = self.subtitle_font_2.render(
            "Make sure your hand is positioned approximately 30 cm from the webcam.", True, white)
        self.subtitle_font_3 = pygame.font.Font(None, 24)
        self.subtitle_text_3 = self.subtitle_font_2.render(
            "Press the spacebar to begin the game.", True, white)
        self.start_rect = self.start_text.get_rect(
            center=(screen_width // 2, screen_height // 2 - 40))
        self.subtitle_rect = self.subtitle_text.get_rect(
            center=(screen_width // 2, screen_height // 2))
        self.subtitle_rect_2 = self.subtitle_text_2.get_rect(
            center=(screen_width // 2, screen_height // 2 + 20))
        self.subtitle_rect_3 = self.subtitle_text_3.get_rect(
            center=(screen_width // 2, screen_height // 2 + 40))

    def display_menu(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    self.show_start_text = False
                    return

            if self.show_start_text:
                screen.fill(white)  # Fill the screen with black background
                screen.blit(self.start_text, self.start_rect)
                screen.blit(self.subtitle_text, self.subtitle_rect)
                screen.blit(self.subtitle_text_2, self.subtitle_rect_2)
                screen.blit(self.subtitle_text_3, self.subtitle_rect_3)
                pygame.display.update()
                clock.tick(60)
                continue  # Skip the rest of the loop until SPACE is pressed
