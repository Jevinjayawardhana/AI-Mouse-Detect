import cv2
import mediapipe as mp
import pyautogui
import pygame
import math

# Initialize Mediapipe Hands
capture_hands = mp.solutions.hands.Hands()
drawing_option = mp.solutions.drawing_utils
screen_width, screen_height = pyautogui.size()

# Initialize Camera
camera = cv2.VideoCapture(0)

# Smoothing variables
smooth_x, smooth_y = 0, 0
smooth_factor = 0.5

# Previous coordinates for click detection
x1 = y1 = x2 = y2 = 0

# Initialize Pygame
pygame.init()
robot_screen_width = 800
robot_screen_height = 600
robot_screen = pygame.display.set_mode((robot_screen_width, robot_screen_height))
pygame.display.set_caption("Robot Arm Simulation")
clock = pygame.time.Clock()

# Define robot arm parameters
robot_arm_color = (0, 255, 0)  # Green color
robot_arm_width = 15
robot_base = (robot_screen_width // 2, robot_screen_height // 2)
robot_arm_length = 150

def draw_robot_arm(screen, base, angle, length):
    end_x = base[0] + int(length * math.cos(math.radians(angle)))
    end_y = base[1] - int(length * math.sin(math.radians(angle)))
    pygame.draw.line(screen, robot_arm_color, base, (end_x, end_y), robot_arm_width)
    pygame.draw.circle(screen, robot_arm_color, (end_x, end_y), 10)  # Draw the end point

while True:
    ret, image = camera.read()
    if not ret:
        break

    image_height, image_width, _ = image.shape
    image = cv2.flip(image, 1)
    rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    output_hands = capture_hands.process(rgb_image)
    all_hands = output_hands.multi_hand_landmarks

    # Handle Pygame events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            camera.release()
            pygame.quit()
            cv2.destroyAllWindows()
            exit()

    if all_hands:
        for hand in all_hands:
            drawing_option.draw_landmarks(image, hand)
            one_handlandmarks = hand.landmark

            for id, lm in enumerate(one_handlandmarks):
                x = int(lm.x * image_width)
                y = int(lm.y * image_height)

                if id == 8:  # Index finger tip
                    mouse_x = (screen_width / image_width * x)
                    mouse_y = (screen_height / image_height * y)

                    # Apply smoothing
                    smooth_x = smooth_factor * mouse_x + (1 - smooth_factor) * smooth_x
                    smooth_y = smooth_factor * mouse_y + (1 - smooth_factor) * smooth_y

                    pyautogui.moveTo(smooth_x, smooth_y)

                    x1, y1 = x, y

                if id == 4:  # Thumb tip
                    x2, y2 = x, y

                    cv2.circle(image, (x, y), 10, (0, 255, 255))

            dist = math.hypot(x2 - x1, y2 - y1)
            if dist < 40:
                pyautogui.click()
                print("Clicked")

            # Update robot arm simulation
            if x1 and y1:
                robot_arm_angle = math.degrees(math.atan2(y1 - robot_base[1], x1 - robot_base[0]))
            else:
                robot_arm_angle = 0

            robot_screen.fill((0, 0, 0))  # Clear the screen with black
            draw_robot_arm(robot_screen, robot_base, robot_arm_angle, robot_arm_length)
            pygame.display.flip()

    cv2.imshow("Hand movement video capture", image)
    key = cv2.waitKey(100)
    if key == 27:  # ESC key to exit
        break

camera.release()
cv2.destroyAllWindows()
pygame.quit()
