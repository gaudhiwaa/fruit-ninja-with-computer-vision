import pygame
import random
import numpy as np
import math
from constants import screen_height, screen_width

class Fruit:
    def __init__(self):
        # Load fruit images from the "Assets/Fruits" folder
        fruit_images = ["Assets/Fruits/apple.png", "Assets/Fruits/banana.png", "Assets/Fruits/orange.png", "Assets/Fruits/pineapple.png", "Assets/Fruits/watermelon.png"]  # Add more fruit images as needed
        self.image_path = random.choice(fruit_images)
        self.image = pygame.image.load(self.image_path)
        self.image = pygame.transform.scale(self.image, (120, 120))
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, screen_width - self.rect.width)
        self.rect.y = screen_height  # Start the fruit at the bottom of the screen
        self.speed = 13  # Adjust the speed value as needed
        self.name = self.image_path.split('/')[-1].split('.')[0]  # Extract fruit name
        self.crossed_center = False  # New flag to track if the fruit crossed the center
        self.velocity = random.uniform(-1, -3)  # Initial negative velocity
        self.gravity = 0.8  # Adjust the gravity value as needed
        self.rotation_angle = random.randint(0, 360)  # Random initial rotation angle
        
        # Adjust the angle based on initial position
        if self.rect.x <= screen_width // 2:
            self.angle = random.choice([90, 85])  # Positive angles for left side
        else:
            self.angle = random.choice([95, 90])  # Negative angles for right side

    def update(self):
        self.rotation_angle = (self.rotation_angle + 2) % 360
        self.velocity += self.gravity
        self.rect.y += self.velocity

        # Calculate horizontal and vertical velocities based on angle
        horizontal_velocity = self.speed * math.cos(math.radians(self.angle))
        vertical_velocity = -self.speed * math.sin(math.radians(self.angle))
        
        self.rect.x += horizontal_velocity
        self.rect.y += vertical_velocity

        if self.crossed_center:
            self.rect.y += self.speed
        else:
            self.rect.y -= self.speed

        # if self.rect.y < 0 or self.rect.y > screen_height:
        #     self.rect.x = random.randint(0, screen_width - self.rect.width)
        #     self.rect.y = screen_height
        #     self.velocity = random.uniform(-1, -3)

    def draw(self, surface):
        rotated_image = pygame.transform.rotate(self.image, self.rotation_angle)
        new_rect = rotated_image.get_rect(center=self.rect.center)
        surface.blit(rotated_image, new_rect)

class CenteredFruit:
    def __init__(self):
        # Load fruit images from the "Assets/Fruits" folder
        fruit_images = ["Assets/Fruits/watermelon.png"]  # Add more fruit images as needed
        self.image_path = random.choice(fruit_images)
        self.name = self.image_path.split('/')[-1].split('.')[0]  # Extract fruit name
        self.image = pygame.image.load(self.image_path)
        self.image = pygame.transform.scale(self.image, (100, 100))
        self.rect = self.image.get_rect()
        self.rect.center = (screen_width // 2, screen_height // 2)  # Place the fruit in the center of the screen
        self.angle = 0  # Initial rotation angle

    def update(self):
        # Increment the rotation angle
        self.angle = (self.angle + 0.5) % 360

    def draw(self, surface):
        # Rotate the image and draw it on the surface
        rotated_image = pygame.transform.rotate(self.image, self.angle)
        new_rect = rotated_image.get_rect(center=self.rect.center)
        surface.blit(rotated_image, new_rect)



