import cv2
import pygame
import time
import random
import pygame.mixer
import numpy as np
from hand_detector import HandDetector
from fruit import Fruit
from constants import screen_height, screen_width, screen, clock, white, red, blue, black, backsound_path
from sound import play_sword_sound

# Initialize pygame mixer
pygame.mixer.init()

backsound = pygame.mixer.Sound(backsound_path)

def main():
    prev_time = 0
    cur_time = 0
    handDetector = HandDetector()
    cap = cv2.VideoCapture(0)
    score = 0
    line_width = 0
    prev_tip_x = 0
    prev_tip_pos = (0, 0)

    # Add more fruit images as needed
    fruit_images = ["apple", "banana", "orange", "watermelon", "pineapple"]

    # Session settings
    session_duration = 2  # 4 seconds per session
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
    subtitle_text = subtitle_font.render(
        "Ensure good lighting—neither too dark nor too bright.", True, white)
    subtitle_font_2 = pygame.font.Font(None, 24)
    subtitle_text_2 = subtitle_font_2.render(
        "Make sure your hand is positioned approximately 30 cm from the webcam.", True, white)
    subtitle_font_3 = pygame.font.Font(None, 24)
    subtitle_text_3 = subtitle_font_2.render(
        "Press the spacebar to begin the game.", True, white)
    start_rect = start_text.get_rect(
        center=(screen_width // 2, screen_height // 2 - 40))
    subtitle_rect = subtitle_text.get_rect(
        center=(screen_width // 2, screen_height // 2))
    subtitle_rect_2 = subtitle_text_2.get_rect(
        center=(screen_width // 2, screen_height // 2 + 20))
    subtitle_rect_3 = subtitle_text_3.get_rect(
        center=(screen_width // 2, screen_height // 2 + 40))
    show_start_text = True

    # Dictionary to track active animations and their start times
    active_animations = {}

    # Load animation images for each fruit
    animation_images = {}

    for fruit_name in fruit_images:
        animation_image_path = f"Assets/FruitSliced/{fruit_name}_splash.png"
        animation_images[fruit_name] = pygame.image.load(animation_image_path)
        animation_images[fruit_name] = pygame.transform.scale(
            animation_images[fruit_name], (100, 100))

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                show_start_text = False
                backsound.play()

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
            # active_fruits.clear()

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
            # if fruit.rect.y > 479:
            #     active_fruits.remove(fruit)

        # Update the display
        pygame.display.update()

        # Convert image to Pygame format
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img_pygame = pygame.surfarray.make_surface(np.rot90(img_rgb))
        img_pygame = pygame.transform.scale(
            img_pygame, (screen_width, screen_height))

        # Draw active fruits and show the image in the Pygame window
        screen.blit(img_pygame, (0, 0))
        for fruit in active_fruits:
            fruit.draw(screen)
            # Check if the fruit is outside the window and hasn't collided
            if not hasattr(fruit, 'collided') and (
                fruit.rect.x == 0 or
                fruit.rect.x > screen_width or
                fruit.rect.y == 0 or
                fruit.rect.y > screen_height
            ):
                fruits_not_colliding += 1  # Increment the counter for non-colliding fruits
                active_fruits.remove(fruit)
                # screen.fill(black)

            # Display fruit coordinates
            # font = pygame.font.Font(None, 24)
            # text = font.render(
            #     f"{fruit.rect.x}, {fruit.rect.y}", True, (255, 255, 255))
            # screen.blit(text, (fruit.rect.x, fruit.rect.y - 30))

        if len(landmarks_list) > 0:
            index_finger_tip_x = landmarks_list[8][1]
            index_finger_tip_y = landmarks_list[8][2]
            # Draw a green dot at the index finger tip position
            pygame.draw.circle(
                screen, (0, 255, 0), (screen_width - index_finger_tip_x, index_finger_tip_y), 15)

            # Draw a white line with sharp edges if the finger tip position has changed significantly
            cur_tip_pos = (screen_width - index_finger_tip_x,
                           index_finger_tip_y)

            offset = random.choice([3, 5, 7])
            
            # Draw a triangle to create sharp edges
            pygame.draw.polygon(screen, white, [
                                    prev_tip_pos, cur_tip_pos, (cur_tip_pos[0] + offset, cur_tip_pos[1] + offset)])
            prev_tip_pos = cur_tip_pos

        font = pygame.font.Font(None, 24)
        text = font.render(
            f"Not collide: {fruits_not_colliding}", True, (255, 255, 255))
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

                    fruit.image = pygame.image.load(half_fruit_image_path)
                    fruit.image = pygame.transform.scale(fruit.image, (80, 80))
                    
                     # Play a random sword sound
                    play_sword_sound()

                    # Start animation effect
                    active_animations[fruit] = time.time()

                    # Increase the score
                    score += 1

        # Update active animations
        for fruit, animation_start_time in list(active_animations.items()):
            animation_duration = 3  # Adjust duration as needed

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
