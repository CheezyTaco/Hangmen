import pygame as pg
import random

words = ["banana", "cherry", "apple"]

def check_ans(char_dict):
    for i in char_dict:
        if i == 0: return False
    return True

def main():
    # Choose a random word
    word = random.choice(words)
    word_size = len(word)

    box_size = 50  # Size of each square box
    gap = 5  # Gap between boxes
    start_x = 100  # Starting x position
    y = 100  # Fixed y position

    # This keep tracks of which player correctly guessed the character at ith index
    # If all integers in points are non-zero, the word is guessed and game will end (for now)
    points = [0] * word_size
    print(word)
    print(points)

    # Create a list to store Rect objects for each box
    boxes = []
    for i, letter in enumerate(word):
        x = start_x + i * (box_size + gap)
        box = pg.Rect(x, y, box_size, box_size)
        boxes.append(box)

    # Initialize Pygame
    pg.init()
    screen = pg.display.set_mode((640, 480))
    font = pg.font.Font(None, 32)
    clock = pg.time.Clock()

    # Colors
    color_inactive = pg.Color('lightskyblue3')
    color_active = pg.Color('dodgerblue2')

    # Track which box is active
    active_box_index = None
    text = [''] * len(word)  # Store text for each box

    done = False
    while not done:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                done = True

            # Handle mouse click
            if event.type == pg.MOUSEBUTTONDOWN:
                # Check if any box was clicked
                for i, box in enumerate(boxes):
                    if box.collidepoint(event.pos):
                        active_box_index = i  # Set the active box
                        break
                else:
                    active_box_index = None  # No box was clicked

            # Handle keyboard input
            if event.type == pg.KEYDOWN:
                if active_box_index is not None:
                    if event.key == pg.K_BACKSPACE:
                        # Remove the last character from the active box
                        text[active_box_index] = text[active_box_index][:-1]
                    elif event.key == pg.K_RETURN:
                        # Submit the word (you can add logic here)
                        print("Submitted word:", ''.join(text))
                    else:
                        # Add the typed character to the active box
                        if len(text[active_box_index]) < 1:  # Limit to one character per box
                            text[active_box_index] += event.unicode

                            if text[active_box_index] == word[active_box_index]:
                                points[active_box_index] = 1
                            else:
                                text[active_box_index] = text[active_box_index][:-1]

                print(points)
                if check_ans(points):
                    print("DONE")
                    done = True
                    break

        # Clear the screen
        screen.fill((30, 30, 30))

        # Draw all boxes
        for i, box in enumerate(boxes):
            color = color_active if i == active_box_index else color_inactive
            pg.draw.rect(screen, color, box, 2)

            # Render the text for the current box
            txt_surface = font.render(text[i], True, color)
            screen.blit(txt_surface, (box.x + 10, box.y + 10))

        # Update the display
        pg.display.flip()
        clock.tick(30)

    # Quit Pygame
    pg.quit()

if __name__ == '__main__':
    main()