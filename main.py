import cv2
import pygame
import time
import random
import pygame.mixer
import numpy as np
from hand_detector import HandDetector
from fruit import Fruit, CenteredFruit
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
    cur_tip_pos = (0, 0)
    line_width = 0
    prev_tip_x = 0
    prev_tip_pos = (0, 0)

    black_cross_image = pygame.image.load("Assets/Cross/black_cross.png")
    red_cross_image = pygame.image.load("Assets/Cross/red_cross.png")

    # Initialize assets
    assets = [black_cross_image] * 3

    # Function to draw assets
    def draw_assets():
        x = 10
        for asset in assets:
            resized_asset = pygame.transform.scale(asset, (50, 50))
            screen.blit(resized_asset, (x, 5))
            x += 50  # Increase the horizontal spacing

    # Menu status
    show_menu = True

    # Sound status
    sound_played = False

    # Game over status
    game_over = False

    sum_fruits = 0

    # Check is main menu fruit has sliced
    menu_fruit_sliced = False

    # Timer after player sliced the fruit
    timer_counter = 0

    # Timer after player game over
    game_over_counter = 0

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

    # Dictionary to track active animations and their start times
    active_animations = {}

    # Load animation images for each fruit
    animation_images = {}

    for fruit_name in fruit_images:
        animation_image_path = f"Assets/FruitSliced/{fruit_name}_splash.png"
        animation_images[fruit_name] = pygame.image.load(animation_image_path)
        animation_images[fruit_name] = pygame.transform.scale(
            animation_images[fruit_name], (130, 130))

    # Fruit in main menu
    centered_fruit = CenteredFruit()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                show_start_text = False
                backsound.play()

        # Timer for fruit in main menu after sliced
        if timer_counter == 50:
            show_menu = False

        if game_over_counter == 300:
            game_over = False
            game_over_counter = 0
            show_menu = True



        # cur_time = time.time()
        # fps = 1 / (cur_time - prev_time)
        # prev_time = cur_time
        # print(f"FPS: {fps:.2f}")

        if show_menu:
            fruits_not_colliding = 0

            # Draw white circle with a hole in the middle
            circle_radius = 80
            circle_thickness = 15
            circle_center = (screen_width // 2, screen_height // 2)

            # Draw outer circle
            pygame.draw.circle(screen, white, circle_center, circle_radius, circle_thickness)

            # Draw title and subtitle
            font_title = pygame.font.Font(None, 45)
            font_subtitle = pygame.font.Font(None, 26)
            title_text = font_title.render("Fruit Ninja with Computer Vision", True, white)
            subtitle_text = font_subtitle.render("Slice the fruit to start the game", True, white)
            title_rect = title_text.get_rect(center=(screen_width // 2, screen_height // 2 - 170))
            subtitle_rect = subtitle_text.get_rect(center=(screen_width // 2, screen_height // 2 - 130))
            screen.blit(title_text, title_rect)
            screen.blit(subtitle_text, subtitle_rect)

            # Update the display
            pygame.display.update()

            # Read video frame from the webcam
            _, img = cap.read()

            # Find hands in the frame and draw landmarks
            img = handDetector.findHands(img)

            # Get landmark positions for a specific hand
            landmarks_list = handDetector.findPosition(img)

             # Convert image to Pygame format
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            img_pygame = pygame.surfarray.make_surface(np.rot90(img_rgb))
            img_pygame = pygame.transform.scale(
                img_pygame, (screen_width, screen_height))

            # Add new fruit at a random interval within the session
            if len(active_fruits) == 0 and not menu_fruit_sliced:
                active_fruits.append(centered_fruit)

            # Draw active fruits and show the image in the Pygame window
            screen.blit(img_pygame, (0, 0))

            if not menu_fruit_sliced:
                centered_fruit.update()
                centered_fruit.draw(screen)

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

            # Update the display
            pygame.display.update()

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
                        # Play a random sword sound
                        play_sword_sound()
                        active_fruits.clear()
                        menu_fruit_sliced = True
                        delattr(fruit, 'collided')

            # Animation after main menu fruit has sliced
            if menu_fruit_sliced:
                active_fruits.clear()
                animation_image = animation_images.get(fruit_name)
                screen.blit(animation_image, fruit.rect)
                pygame.display.update()
                timer_counter += 1


            # print(show_menu, game_over, len(active_fruits), menu_fruit_sliced, timer_counter)
            

        # start game
        elif not show_menu and not game_over and (len(active_fruits) == 0 or (menu_fruit_sliced and timer_counter == 50)):

            print("YESS")
            
            if not sound_played:
                # backsound.play()
                sound_played = True

            # Calculate session time
            elapsed_time = time.time() - session_start_time

            # Check if the session has ended
            if elapsed_time >= session_duration:
                # Reset session settings
                session_start_time = time.time()
                fruits_dropped = 0

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
                    sum_fruits += 1
                    fruits_dropped += 1

            # Update and draw active fruits
            for fruit in active_fruits:
                fruit.update()

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
                    fruit.rect.x < 0 or
                    fruit.rect.x > screen_width - 90 or
                    fruit.rect.y > screen_height
                ):
                    # Increment the counter for non-colliding fruits
                    fruits_not_colliding += 1  
                    assets = [red_cross_image] * fruits_not_colliding  + [black_cross_image] * (3-fruits_not_colliding)
                    active_fruits.remove(fruit)

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

            # font = pygame.font.Font(None, 24)
            # text = font.render(
            #     f"Not collide: {fruits_not_colliding}", True, (255, 255, 255))
            # screen.blit(text, (10, 10))

            # Check if the maximum number of not collided fruits is reached
            if fruits_not_colliding >= 3:
                game_over = True

            # Draw how many not colliding fruit
            draw_assets()

            # Display the score
            font = pygame.font.Font(None, 36)
            score_text = font.render(f"Score: {score}", True, white)
            score_rect = score_text.get_rect(topright=(screen_width - 10, 10))
            screen.blit(score_text, score_rect)

            # Update the display
            pygame.display.update()

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
                        fruit.image = pygame.transform.scale(fruit.image, (110, 110))
                        
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
                    animation_image = animation_images.get(fruit.name)

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

        elif game_over:
                # Fill the screen with green color
                screen.fill((0, 0, 0)) 

                # Display "Game Over" message
                font_game_over = pygame.font.Font(None, 72)
                game_over_text = font_game_over.render("Game Over", True, (255, 0, 0))
                game_over_rect = game_over_text.get_rect(center=(screen_width // 2, screen_height // 2))
                screen.blit(game_over_text, game_over_rect)

                # Display total score
                font_total_score = pygame.font.Font(None, 36)
                total_score_text = font_total_score.render(f"Total Score: {score}", True, (255, 255, 255))
                total_score_rect = total_score_text.get_rect(midtop=(screen_width // 2, game_over_rect.bottom + 20))
                screen.blit(total_score_text, total_score_rect)

                # Update the display
                pygame.display.update()

                timer_counter = 0

                menu_fruit_sliced = False

                active_fruits = []

               
                game_over_counter +=1

                assets = [black_cross_image] * 3

        clock.tick(60)
        
if __name__ == "__main__":
    main()
