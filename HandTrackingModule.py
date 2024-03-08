import cv2
import mediapipe as mp
import time
import pygame
import random
import numpy as np
import math

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

# Fruit class
class Fruit:
    def __init__(self):
        # Load fruit images from the "Assets/Fruits" folder
        fruit_images = ["Assets/Fruits/apple.png", "Assets/Fruits/banana.png", "Assets/Fruits/orange.png"]  # Add more fruit images as needed
        self.image_path = random.choice(fruit_images)
        self.image = pygame.image.load(self.image_path)
        self.image = pygame.transform.scale(self.image, (80, 80))
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
            self.angle = random.choice([40, 50])  # Positive angles for left side
        else:
            self.angle = random.choice([130, 140])  # Negative angles for right side

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

        if self.rect.y < 0 or self.rect.y > screen_height:
            self.rect.x = random.randint(0, screen_width - self.rect.width)
            self.rect.y = screen_height
            self.velocity = random.uniform(-1, -3)

    def draw(self, surface):
        rotated_image = pygame.transform.rotate(self.image, self.rotation_angle)
        new_rect = rotated_image.get_rect(center=self.rect.center)
        surface.blit(rotated_image, new_rect)

class HandDetector():
    def __init__(self, mode=False, max_hands=2, detectionCon=0.7, trackCon=0.5):
        self.mode = mode
        self.max_hands = max_hands
        self.detectionCon = detectionCon
        self.trackCon = trackCon
        
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(self.mode, self.max_hands, self.detectionCon, self.trackCon)
        self.mp_draw = mp.solutions.drawing_utils
        self.tipIds = [4, 8, 12, 16, 0]  # Finger tip IDs for thumb and fingers

    def findHands(self, img, draw=True):
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(imgRGB)
        
        if self.results.multi_hand_landmarks:
            for hand_landmarks in self.results.multi_hand_landmarks:
                if draw:
                    self.mp_draw.draw_landmarks(img, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)
        return img

    def findPosition(self, img, handNo=0, draw=True):
        self.landmark_list = []
        if self.results.multi_hand_landmarks:
            my_hand = self.results.multi_hand_landmarks[handNo]
            for index, lm in enumerate(my_hand.landmark):
                height, width, channel = img.shape
                cx, cy = int(lm.x * width), int(lm.y * height)
                self.landmark_list.append([index, cx, cy])
                if draw:
                    cv2.circle(img, (cx, cy), 10, (255, 0, 255), cv2.FILLED)
        return self.landmark_list

    def fingersUp(self):
        fingers = []

        # Thumb
        if self.landmark_list[self.tipIds[0]][1] < self.landmark_list[self.tipIds[0] - 1][1]:
            fingers.append(1)
        else:
            fingers.append(0)

        # Other 4 fingers
        for id in range(1, 5):
            if self.landmark_list[self.tipIds[id]][2] < self.landmark_list[self.tipIds[id] - 2][2]:
                fingers.append(1)
            else:
                fingers.append(0)
        return fingers

def main():
    prev_time = 0
    cur_time = 0
    handDetector = HandDetector()
    cap = cv2.VideoCapture(0)
    score = 0
    fruit_images = ["apple", "banana", "orange"]  # Add more fruit images as needed

    # Session settings
    session_duration = 8 # 4 seconds per session
    session_start_time = time.time()
    fruits_dropped = 0
    max_fruits_per_session = 5  # Maximum 4 fruits per session

    # List to store active fruits
    active_fruits = []

     # Counter for fruits that are not colliding and are outside of the screen
    fruits_not_colliding = 0

    # Initialize finger coordinates
    index_finger_tip_x = 0
    index_finger_tip_y = 0
    
    # Display "Start Game" text
    start_font = pygame.font.Font(None, 36)
    start_text = start_font.render("Start Game", True, white)
    subtitle_font = pygame.font.Font(None, 24)
    subtitle_text = subtitle_font.render("Ensure good lighting—neither too dark nor too bright.", True, white)
    subtitle_font_2 = pygame.font.Font(None, 24)
    subtitle_text_2 = subtitle_font_2.render("Make sure your hand is positioned approximately 30 cm from the webcam.", True, white)
    subtitle_font_3 = pygame.font.Font(None, 24)
    subtitle_text_3 = subtitle_font_2.render("Press the spacebar to begin the game.", True, white)
    start_rect = start_text.get_rect(center=(screen_width // 2, screen_height // 2 - 40))
    subtitle_rect = subtitle_text.get_rect(center=(screen_width // 2, screen_height // 2))
    subtitle_rect_2 = subtitle_text_2.get_rect(center=(screen_width // 2, screen_height // 2 + 20))
    subtitle_rect_3 = subtitle_text_3.get_rect(center=(screen_width // 2, screen_height // 2 + 40))
    show_start_text = True

    # Dictionary to track active animations and their start times
    active_animations = {}

    # Load animation images for each fruit
    animation_images = {}

    for fruit_name in fruit_images:
        animation_image_path = f"Assets/FruitSliced/{fruit_name}_splash.png"
        animation_images[fruit_name] = pygame.image.load(animation_image_path)
        animation_images[fruit_name] = pygame.transform.scale(animation_images[fruit_name], (80, 80))

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                show_start_text = False

        if show_start_text:
            screen.fill(black)  # Fill the screen with black background
            screen.blit(start_text, start_rect)
            screen.blit(subtitle_text, subtitle_rect)
            screen.blit(subtitle_text_2, subtitle_rect_2)
            screen.blit(subtitle_text_3, subtitle_rect_3)
            pygame.display.update()
            clock.tick(60)
            continue  # Skip the rest of the loop until SPACE is pressed

        # Calculate session time
        elapsed_time = time.time() - session_start_time

        # Check if the session has ended
        if elapsed_time >= session_duration:
            # Reset session settings
            session_start_time = time.time()
            fruits_dropped = 0
            active_fruits.clear()

        # Read video frame from the webcam
        _, img = cap.read()
        # img = cv2.flip(img, 1)

        # Find hands in the frame and draw landmarks
        img = handDetector.findHands(img)
        # Get landmark positions for a specific hand
        landmarks_list = handDetector.findPosition(img)

        # Add new fruit at a random interval within the session
        if elapsed_time < session_duration and fruits_dropped < max_fruits_per_session:
            if random.randint(0, 100) < 5:  # Adjust the probability
                active_fruits.append(Fruit())
                fruits_dropped += 1

        # Update and draw active fruits
        for fruit in active_fruits:
            fruit.update()
            if fruit.rect.y > 479:
                active_fruits.remove(fruit)

        # Update the display
        pygame.display.update()

        # Convert image to Pygame format
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img_pygame = pygame.surfarray.make_surface(np.rot90(img_rgb))
        img_pygame = pygame.transform.scale(img_pygame, (screen_width, screen_height))

        # Draw active fruits and show the image in the Pygame window
        screen.blit(img_pygame, (0, 0))
        for fruit in active_fruits:
            fruit.draw(screen)
            # Check if the fruit is outside the window and hasn't collided
            if not hasattr(fruit, 'collided') and (
                fruit.rect.x == 0 or 
                fruit.rect.x == screen_width or
                fruit.rect.y == 0 or
                fruit.rect.y == screen_height
            ):
                fruits_not_colliding += 1  # Increment the counter for non-colliding fruits
                # screen.fill(black)
                
            # Display fruit coordinates
            font = pygame.font.Font(None, 24)
            text = font.render(f"{fruit.rect.x}, {fruit.rect.y}", True, (255, 255, 255))
            screen.blit(text, (fruit.rect.x, fruit.rect.y - 30))

        # Display index finger coordinates
        if len(landmarks_list) > 0:
            index_finger_tip_x = landmarks_list[8][1]
            index_finger_tip_y = landmarks_list[8][2]
            # Draw a green dot at the index finger tip position
            pygame.draw.circle(screen, (0, 255, 0), (screen_width-index_finger_tip_x, index_finger_tip_y), 15)
            
        font = pygame.font.Font(None, 24)
        text = font.render(f"Not collide: {fruits_not_colliding}", True, (255, 255, 255))
        screen.blit(text, (10, 10))

        # Display the score
        font = pygame.font.Font(None, 36)
        score_text = font.render(f"Score: {score}", True, white)
        score_rect = score_text.get_rect(topright=(screen_width - 10, 10))
        screen.blit(score_text, score_rect)

        # Update the display
        pygame.display.update()

        cur_time = time.time()
        fps = 1 / (cur_time - prev_time)
        prev_time = cur_time
        print(f"FPS: {fps:.2f}")

        # Check for collision with index finger
        for fruit in active_fruits:
            if not hasattr(fruit, 'collided'):  # Check if fruit has already collided
                tolerance = 10
                collision = False
                for dx in range(-tolerance, tolerance + 1):
                    for dy in range(-tolerance, tolerance + 1):
                        if fruit.rect.collidepoint(screen_width - index_finger_tip_x + dx, index_finger_tip_y + dy) and len(landmarks_list) != 0:
                            collision = True
                            fruit.collided = True  # Mark the fruit as collided
                            break
                    if collision:
                        break

                if collision:
                    # Load half fruit image based on fruit name
                    half_fruit_image_path = f"Assets/HalfFruits/{fruit.name}_half_{random.choice(['1', '2'])}.png"
                    
                    # Load animation image based on fruit name
                    half_fruit_animation_path = f"Assets/FruitSliced/{fruit.name}_splash.png"
                    
                    fruit.image = pygame.image.load(half_fruit_image_path)
                    fruit.image = pygame.transform.scale(fruit.image, (80, 80))
                    
                    # Start animation effect
                    active_animations[fruit] = time.time()
                    
                    # Increase the score
                    score += 1
        
        # Update active animations
        for fruit, animation_start_time in list(active_animations.items()):
            animation_duration = 0.9  # Adjust duration as needed
            
            if time.time() - animation_start_time < animation_duration:
                # Load animation image and draw it
                fruit_name = fruit.name
                animation_image = animation_images.get(fruit_name)
                if animation_image:
                    screen.blit(animation_image, fruit.rect)
                    pygame.display.update()
            else:
                # Animation duration passed, remove from active_animations
                del active_animations[fruit]

        # Break the loop if 'q' key is pressed
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

        clock.tick(60)

if __name__ == "__main__":
    main()



