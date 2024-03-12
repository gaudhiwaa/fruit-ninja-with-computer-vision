import pygame

# Initialize pygame
pygame.init()

# Screen dimensions
screen_width = 640
screen_height = 480
screen = pygame.display.set_mode((screen_width, screen_height))

# Clock for controlling frame rate
clock = pygame.time.Clock()

# Colors
white = (255, 255, 255)
red = (255, 0, 0)
blue = (0, 0, 255)
black = (0, 0, 0)

# List of sword sound paths
sword_sounds_path = [
    "Assets/SwordSound/sword_sound_1.mp3",
    "Assets/SwordSound/sword_sound_2.mp3",
]

# Background sound paths
backsound_path = "Assets/Backsound/backsound.mp3"