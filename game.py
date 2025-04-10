import os
import sys
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame as pg
import random
import time
from Client import *

SERVER_IP = sys.argv[1]
PORT = 5555
REQUEST_RATE = 0.25


# Takes a point array and checks if each character is correctly guessed.
def check_ans(char_dict):
    for i in char_dict:
        if i == "":
            return False
    return True


def main():
    # Connect to the server

    global SERVER_IP
    global PORT
    global REQUEST_RATE

    sfd = Connect(SERVER_IP, PORT)

    # receive assigned id from server
    my_id = int(sfd.recv(1024).decode("utf-8"))

    print("Connected to server. Server gave me id", my_id)

    # Client receives a state with word size, client count, and box states
    (word_size, _, states) = Request_State(sfd)

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

    # Initialize Pygame
    pg.init()
    screen = pg.display.set_mode((640, 480))
    font = pg.font.Font(None, 50)
    clock = pg.time.Clock()

    client_names = ["red", "yellow", "green", "orange"]
    # Colors
    client_colors = [pg.Color(name) for name in client_names]
    color_inactive = pg.Color("darkgray")

    # Track which box is active (which box is the player currently typing in)
    active_box_index = None

    # Store text for each box individual box and the full box in the same list
    text = [""] * (word_size * 2)

    last_update_at = 0

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
                        if active_box_index < word_size:
                            text[active_box_index] = ""
                        else:
                            text[word_size:] = [""] * word_size
                    Unlock_Box(sfd)
                    active_box_index = None
                elif not Have_Box(sfd, str(collided_index)):
                    # if we don't have the box, unlock any held box and try to get it
                    Unlock_Box(sfd)
                    if Request_Box(sfd, str(collided_index)):
                        active_box_index = min(collided_index, word_size)
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
                            Guess(
                                sfd,
                                min(active_box_index, word_size),
                                text[active_box_index],
                            )
                            # after submitting a guess, we lose the box
                            active_box_index = None
                        elif active_box_index == len(text) - 1:
                            # submit full word guess
                            Guess(
                                sfd,
                                active_box_index,
                                "".join(text[word_size:]),
                            )
                            active_box_index = None
                    case _:
                        if not event.unicode.isalpha():
                            break

                        # Add the typed character to the active box
                        if text[active_box_index] == "":
                            text[active_box_index] = event.unicode.lower()
                            if active_box_index in range(word_size, word_size * 2 - 1):
                                active_box_index += 1

        # Clear the screen
        screen.fill((30, 30, 30))

        # Get state update from server (limit request rate to avoid overloading server)
        if time.monotonic() - last_update_at > REQUEST_RATE:
            (_, client_cnt, states) = Request_State(sfd)

            for i, (_, contents, owner_id) in enumerate(states):
                if contents == "" and owner_id != my_id:
                    if i == word_size:
                        text[word_size:] = [""] * word_size
                    else:
                        text[i] = ""

                    if active_box_index is not None and min(i, word_size) == min(
                        active_box_index, word_size
                    ):
                        active_box_index = None

            # Check if game won
            letter_boxes_state = [i for (_, i, _) in states]
            (_, full_box_state, _) = states[word_size]
            if check_ans(letter_boxes_state[:-1]) or full_box_state != "":
                print("\nThe game was won!")
                if (check_ans(letter_boxes_state[:-1])):
                    print("The word was "+ "".join(letter_boxes_state[:-1]))
                else:
                    print("The word was "+ full_box_state)
                points = [
                    sum([1 for (c, _, _) in states[:-1] if c == i])
                    for i in range(client_cnt)
                ]
                full_box_winner = states[-1][0]
                if full_box_winner != -1:
                    points[full_box_winner] += word_size - sum(points)

                for i, name in enumerate(client_names[:client_cnt]):
                    print(name, ":", int(points[i] * 100 / word_size), "points")

                done = True

            last_update_at = time.monotonic()

        # Draw all boxes
        for i, box in enumerate(boxes):
            (correct_guesser_id, contents, owner_id) = states[min(i, word_size)]
            color = color_inactive

            if correct_guesser_id != -1:
                color = client_colors[correct_guesser_id]
            elif owner_id != -1:
                color = client_colors[owner_id]

            pg.draw.rect(screen, color, box, 2)

            # Render text from the game state
            if contents != "":
                if i < word_size:
                    txt_surface = font.render(contents, True, color)
                else:
                    txt_surface = font.render(contents[i - word_size], True, color)
                screen.blit(txt_surface, (box.x + 15, box.y + 8))

            # Render text typed out by player
            if text[i] != "":
                txt_surface = font.render(text[i], True, (255, 255, 255))
                screen.blit(txt_surface, (box.x + 15, box.y + 8))

        # Update the display
        pg.display.flip()
        clock.tick(30)

    # Quit Pygame
    pg.quit()
    sfd.close()


if __name__ == "__main__":
    main()
