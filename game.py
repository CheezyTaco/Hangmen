import pygame as pg
import random
import time
from Client import *

words = ["banana", "cherry", "apple"]
serverIP = "127.0.0.1"
port = 5555


# Takes a point array and checks if each character is correctly guessed.
def check_ans(char_dict):
    for i in char_dict:
        if i == '-':
            return False
    return True


def main():
    # Connect to the server

    global serverIP
    global port
    sfd = Connect(serverIP, port)
    print("Connected to server")

    # Client receives a skeleton for the word
    points = Request_Update(sfd)
    word_size = len(points)  # Size of word
    print(word_size)

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
    text = [""] * (
        word_size * 2
    )  # Store text for each box individual box, and the full box

    last_update_request = 0

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
                    collided_lock_index = min(collided_index, word_size)

                    # do we already have the lock for this box?
                    if active_box_index is None or collided_lock_index != min(
                        active_box_index, word_size
                    ):
                        # if we don't have the lock, lose old locks and try to get it
                        Unlock_Box(sfd)
                        if Request_Box(sfd, str(collided_lock_index)):
                            print("got lock ", collided_index)
                            active_box_index = collided_index
                        else:
                            active_box_index = None

            # Handle keyboard input
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_BACKSPACE:
                    if active_box_index is not None:
                        text[active_box_index] = ""
                        if active_box_index > word_size:
                            active_box_index -= 1
                elif event.key == pg.K_RETURN:
                    if active_box_index is not None:
                        if active_box_index < word_size:
                            # submit letter guess
                            print(text[active_box_index])
                            Guess(
                                sfd,
                                text[active_box_index],
                                min(active_box_index, word_size),
                            )
                            text[active_box_index] = ""
                            active_box_index = None
                        elif active_box_index == len(text) - 1:
                            # submit full word guess
                            Guess(
                                sfd, ''.join(text[word_size:]), min(active_box_index, word_size)
                            )
                            text[word_size:] = [""] * word_size
                            active_box_index = None
                else:
                    # Add the typed character to the active box
                    if (
                        active_box_index is not None
                        and text[active_box_index] == ""
                        and event.unicode.isalpha()
                    ):
                        text[active_box_index] = event.unicode
                        if active_box_index in range(word_size, 2 * word_size - 1):
                            active_box_index += 1

        # Clear the screen
        screen.fill((30, 30, 30))

        # Update letter boxes (limit requests to every 250ms to avoid overloading server)
        if time.monotonic_ns() - last_update_request > 250000000:
            points = Request_Update(sfd)
            for i in range(word_size):
                if points[i] != "-":
                    text[i] = points[i]

            print(points)

            if check_ans(points):
                done = True

            last_update_request = time.monotonic_ns()

        # Draw all boxes
        for i, box in enumerate(boxes):
            color = (
                color_active
                if active_box_index is not None
                and min(i, word_size) == min(active_box_index, word_size)
                else color_inactive
            )
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


if __name__ == "__main__":
    main()
