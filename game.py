import pygame as pg
import random
import time
from Client import *

words = ["banana", "cherry", "apple"]
SERVER_IP = "127.0.0.1"
PORT = 5555
REQUEST_RATE = 0.25


# Takes a point array and checks if each character is correctly guessed.
def check_ans(char_dict):
    for i in char_dict:
        if i == "-":
            return False
    return True


def main():
    # Connect to the server

    global SERVER_IP
    global PORT
    sfd = Connect(SERVER_IP, PORT)
    print("Connected to server")

    # Client receives a skeleton for the word
    guess_state = Request_Update(sfd)
    word_size = len(guess_state)  # Size of word
    print(word_size)

    # Converts a box index to a lock index (boxes >= word_size correspond to the full box lock)
    def box_to_lock(box_index):
        return min(box_index, word_size)

    # Tell server that the player is ready
    # client_Ready(sfd, name)

    box_size = 50  # Size of each square box
    gap = 5  # Gap between boxes
    start_x = 100  # Starting x position
    y = 100  # Fixed y position
    y_fullbox = 300

    # Create a list to store Rect objects for each character box
    boxes = []
    for i in range(word_size):
        x = start_x + i * (box_size + gap)
        box = pg.Rect(x, y, box_size, box_size)
        boxes.append(box)

    # Add full box boxes after individual boxes (box with index >= word_size is in full box)
    for i in range(word_size):
        x = start_x + i * (box_size + gap)
        box = pg.Rect(x, y_fullbox, box_size, box_size)
        boxes.append(box)

    print(len(boxes))

    # Initialize Pygame
    pg.init()
    screen = pg.display.set_mode((640, 480))
    font = pg.font.Font(None, 32)
    clock = pg.time.Clock()

    # Colors
    color_inactive = pg.Color("lightskyblue3")
    color_active = pg.Color("dodgerblue2")

    # Track which box is active (which box has this player earned the lock)
    active_box_index = None

    # Store text for each box individual box and the full box in the same list
    text = [""] * (word_size * 2)

    last_update_at = 0
    box_locked_at = 0

    my_points = 0
    others_points = 0

    # Game loop
    print("Game initialized")
    done = False

    while not done:

        for event in pg.event.get():
            if event.type == pg.QUIT:
                done = True

            # Handle mouse click
            if event.type == pg.MOUSEBUTTONDOWN:

                # Check for collisions with a box
                collided_index = None
                for i, box in enumerate(boxes):
                    if box.collidepoint(event.pos):
                        collided_index = i
                        break

                if collided_index is None:
                    # clicked outside of any box
                    if active_box_index is not None:
                        Unlock_Box(sfd)
                    active_box_index = None
                else:
                    # clicked into a box
                    collided_lock_index = box_to_lock(collided_index)

                    # do we already have the lock for this box?
                    if active_box_index is None or collided_lock_index != box_to_lock(
                        active_box_index
                    ):
                        # if we don't have the lock, lose old locks and try to get it
                        Unlock_Box(sfd)
                        if Request_Box(sfd, str(collided_lock_index)):
                            print("got lock ", collided_index)
                            box_locked_at = time.monotonic()
                            active_box_index = collided_index
                        else:
                            active_box_index = None

            # Handle keyboard input
            elif event.type == pg.KEYDOWN and active_box_index is not None:
                match event.key:
                    case pg.K_BACKSPACE:
                        if text[active_box_index] != "":
                            text[active_box_index] = ""
                        elif active_box_index > word_size:
                            active_box_index -= 1
                            text[active_box_index] = ""

                    case pg.K_RETURN:
                        if active_box_index < word_size:
                            # submit letter guess
                            print(text[active_box_index])
                            if Guess(
                                sfd,
                                text[active_box_index],
                                min(active_box_index, word_size),
                            ):
                                my_points += 1
                            text[active_box_index] = ""
                            active_box_index = None
                        elif active_box_index == len(text) - 1:
                            # submit full word guess
                            if Guess(
                                sfd,
                                "".join(text[word_size:]),
                                box_to_lock(active_box_index),
                            ):
                                my_points += word_size - others_points
                            text[word_size:] = [""] * word_size
                            active_box_index = None
                    case _:
                        if not event.unicode.isalpha():
                            break

                        # Add the typed character to the active box
                        if text[active_box_index] == "":
                            text[active_box_index] = event.unicode
                            if active_box_index in range (word_size, word_size * 2 - 1):
                                active_box_index += 1

        # Clear the screen
        screen.fill((30, 30, 30))

        # timeout lock after 5 seconds
        if active_box_index is not None and time.monotonic() - box_locked_at > 5:
            if active_box_index in range(word_size, word_size *2):
                text[word_size:] = [""] * word_size
            else:
                text[active_box_index] = ""
            active_box_index = None

        # Update letter boxes (limit requests to avoid overloading server)
        if time.monotonic() - last_update_at > REQUEST_RATE:
            guess_state = Request_Update(sfd)

            left_to_guess = 0
            for i in range(word_size):
                if guess_state[i] != "-":
                    text[i] = guess_state[i]
                else:
                    left_to_guess += 1

            others_points = word_size - left_to_guess - my_points

            print(guess_state)

            if check_ans(guess_state):
                print("The game was won!")
                print("You have", int(my_points * 100 / word_size), "points")
                done = True

            last_update_at = time.monotonic()

        # Draw all boxes
        for i, box in enumerate(boxes):
            color = color_inactive
            if active_box_index is not None and box_to_lock(i) == box_to_lock(
                active_box_index
            ):
                color = color_active

            pg.draw.rect(screen, color, box, 2)

            # Render the text for the current box
            if text[i] != "":
                txt_surface = font.render(text[i], True, (255, 255, 255))
                screen.blit(txt_surface, (box.x + 10, box.y + 10))

        # Update the display
        pg.display.flip()
        clock.tick(30)

    # Quit Pygame
    pg.quit()
    sfd.close()


if __name__ == "__main__":
    main()
