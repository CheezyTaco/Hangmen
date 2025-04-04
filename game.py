import pygame as pg
import random
from Client import *

words = ["banana", "cherry", "apple"]
serverIP = '127.0.0.1'
port = 5555

# Takes a point array and checks if each character is correctly guessed.
def check_ans(char_dict):
    for i in char_dict:
        if i == 0: return False
    return True


def main():
    # Connect to the server
    
    global serverIP
    global port
    sfd = Connect(serverIP, port)
    print("Connected to server")

    # Client receives the random word from Server
    word = Get_Word(sfd)

    # Tell server that the player is ready
    # client_Ready(sfd, name)

    word_size = len(word)  # Size of word          // server side variable?

    box_size = 50  # Size of each square box
    gap = 5  # Gap between boxes
    start_x = 100  # Starting x position
    y = 100  # Fixed y position
    y_fullbox = 300

    # This keep tracks of which player correctly guessed the character at ith index
    # If all integers in points are non-zero, the word is guessed and game will end (for now)
    points = [0] * word_size  # Server side variable?

    # This is for guessing a word as a whole
    fullbox_points = [0] * word_size  # Server side variable?

    print(word)
    print(points)

    # Create a list to store Rect objects for each character box
    boxes = []
    for i, letter in enumerate(word):
        x = start_x + i * (box_size + gap)
        box = pg.Rect(x, y, box_size, box_size)
        boxes.append(box)

    # Create a list to store Rect objects for whole word guess
    fullbox = []
    for i, letter in enumerate(word):
        x = start_x + i * (box_size + gap)
        box = pg.Rect(x, y_fullbox, box_size, box_size)
        fullbox.append(box)

    # Initialize Pygame
    pg.init()
    screen = pg.display.set_mode((640, 480))
    font = pg.font.Font(None, 32)
    clock = pg.time.Clock()

    # Colors
    color_inactive = pg.Color('lightskyblue3')
    color_active = pg.Color('dodgerblue2')

    # Track which box is active (which box has this player earned the lock)
    active_box_index = None
    text = [''] * len(word)  # Store text for each box
    fullbox_text = [''] * len(word)
    fullbox_active = False

    # Game loop
    print("Game initialized")
    done = False

    while not done:

        for event in pg.event.get():
            if event.type == pg.QUIT:
                done = True

            # Handle mouse click
            if event.type == pg.MOUSEBUTTONDOWN:
                Unlock_Box(sfd)
                active_box_index = None

                # Fills guessed characters in each box
                for i in range(len(fullbox_text)):
                    fullbox_text[i] = ''
                for i in range(len(text)):
                    if text[i]:
                        fullbox_text[i] = text[i]

                # Check if any box was clicked
                for i, box in enumerate(boxes):
                    if box.collidepoint(event.pos):

                        # Client calls to check if this box is available
                        if (Request_Box(sfd, str(i))):
                            fullbox_active = False
                            active_box_index = i  # Set the active box
                            break
                        else:
                            print("Box already taken")
                    else:
                        active_box_index = None  # No box was clicked

                # Check if user clicked fullbox
                if active_box_index is None:

                    # Client call to check if the fullbox is available
                    # if (Request_Box(sfd, i)):

                    for i, box in enumerate(fullbox):
                        if box.collidepoint(event.pos):
                            # Erases any characters on fullbox when typing the guess for whole word
                            for i in range(len(fullbox_text)):
                                fullbox_text[i] = ''
                            fullbox_active = True
                            break
                        else:
                            fullbox_active = False

            # Handle keyboard input
            if event.type == pg.KEYDOWN:
                if active_box_index is not None:
                    if event.key == pg.K_BACKSPACE:
                        # Remove the last character from the active box
                        text[active_box_index] = text[active_box_index][:-1]
                    elif event.key == pg.K_RETURN:
                        # What to do if user presses enter key? (Not necessary to handle this)
                        print("Submitted word:", ''.join(text))
                    else:
                        # Add the typed character to the active box
                        if len(text[active_box_index]) < 1:  # Limit to one character per box
                            text[active_box_index] += event.unicode

                            if text[active_box_index] == word[active_box_index]:  # The guess is correct

                                # Client call to send updates to all players for correctly guessed character
                                Guess(sfd, word[active_box_index], str(active_box_index))

                                points[active_box_index] = 1
                                fullbox_text[active_box_index] += event.unicode

                                # Client call to release box? // after Guess function, server can release it

                            else:  # The guessed character is incorrect
                                text[active_box_index] = text[active_box_index][:-1]

                # If user chose the fullbox
                elif fullbox_active is True:
                    if event.unicode.isalpha():
                        for i in range(len(fullbox_text)):
                            if not fullbox_text[i]:
                                fullbox_text[i] = event.unicode
                                if fullbox_text[i] == word[i]:
                                    fullbox_points[i] = 1

                                break

                # Should the server check the answers?

                if check_ans(
                        points):  # Checks if each character box are correctly guessed. End the game if they are all guessed correctly.
                    print("DONE")
                    done = True
                    guessing_fullbox_points = fullbox_points.count(1) - points.count(1)
                    print("FULLBOX GUESSER WON " + str(guessing_fullbox_points) + " POINTS")
                    break

                if check_ans(
                        fullbox_points):  # Checks if the fullbox is correctly guessed. End the game if it is guessed correctly.
                    print("DONE")
                    guessing_fullbox_points = fullbox_points.count(1) - points.count(1)
                    print("FULLBOX GUESSER WON " + str(guessing_fullbox_points) + " POINTS")
                    done = True
                    break

                print(points)
                print(guessed_box)

        # Clear the screen
        screen.fill((30, 30, 30))

        # Update 'text' and 'fullbox_text' with boxes
        guessed_box = Request_Update(sfd)
        for i in range(word_size):
            if int(guessed_box[i]) != 0:
                points[i] = 1
                text[i] = word[i]
        
        # Draw all boxes
        for i, box in enumerate(boxes):
            color = color_active if i == active_box_index else color_inactive
            pg.draw.rect(screen, color, box, 2)

            # Render the text for the current box
            if points[i]:
                txt_surface = font.render(text[i], True, (255, 255, 255))
                screen.blit(txt_surface, (box.x + 10, box.y + 10))

        for i, box in enumerate(fullbox):
            color = color_active if fullbox_active is True else color_inactive
            pg.draw.rect(screen, color, box, 2)
            if fullbox_text[i]:  # Only render if there's a correct letter
                txt_surface = font.render(fullbox_text[i], True, (255, 255, 255))  # White text
                screen.blit(txt_surface, (box.x + 10, box.y + 10))

        # Update the display
        pg.display.flip()
        clock.tick(30)

    # Quit Pygame
    pg.quit()


if __name__ == '__main__':
    main()

