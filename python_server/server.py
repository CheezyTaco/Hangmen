import socket
import threading

from Dict import *
from Box import *

MIN_WORD_LEN = 4
MAX_WORD_LEN = 10

boxes = []  # locks for each character box
connected_count = 0
max_connected_count = 0
connected_count_lock = threading.Lock()
stop_running = False
server_socket = None

def init_game():
    global boxes

    # get a random word from the dictionary with a length in the range [6,8]
    the_word = Dict("test_dictionary.txt").get_random_word(6, 8)
    # the_word = Dict("dictionary.txt").get_random_word(6, 8)

    print("word:", the_word)

    # initialize boxes with the word
    boxes = [Box(c) for c in the_word]  # individual letter boxes
    boxes.append(Box(the_word))  # full word box


def handle_client(client_socket, address):
    global max_connected_count
    global connected_count
    global boxes

    print(f"[+] New connection from {address}")

    # send the client its id (use the current connection count as id)
    try:
        with connected_count_lock:
            client_id = connected_count
            client_socket.send((f"%s" % client_id).encode("utf-8"))
            connected_count += 1

            # keep track of the max number of connections, so clients can know how
            # many other clients are/were in the game
            max_connected_count = max(connected_count, max_connected_count)
    except ConnectionResetError:
        client_socket.close()
        return

    while True:
        try:
            # Receive a message from a player
            message = client_socket.recv(1024).decode("utf-8")
            if not message:
                break

            # split the message
            message = message.strip().split(",")

            token_name = message[0]

            # Request box message (message[1]: the ith box)
            if token_name == "Request_Box":
                box = boxes[min(int(message[1]), len(boxes) - 1)]
                response = f"1" if box.request(client_id) else f"0"
                client_socket.send(response.encode("utf-8"))

            # Have box message (message[1]: the ith box)
            elif token_name == "Have_Box":
                box = boxes[min(int(message[1]), len(boxes) - 1)]
                response = f"1" if box.is_owner(client_id) else f"0"
                client_socket.send(response.encode("utf-8"))

            # Guess message (message[1]: the ith box, message[2]: the guess)
            elif token_name == "Guess":
                box = boxes[min(int(message[1]), len(boxes) - 1)]
                response = f"1" if box.submit_guess(client_id, message[2]) else f"0"
                client_socket.send(response.encode("utf-8"))

            # Request_Update message: send the game state to the client, so it
            # knows who owns which box, and which boxes have been correctly guessed
            elif token_name == "Request_State":
                response = f"%s,%s" % (
                    (len(boxes) - 1),
                    max_connected_count,
                )  # word size and client count
                for box in boxes:
                    box.update_timeout()
                    with box.lock:
                        response += ","
                        if box.correct_guesser is not None:
                            response += (
                                str(box.correct_guesser) + "," + box.contents
                            )  # correct guesser and contents for this box
                        else:
                            response += "-1,"  # no correct guess yet

                        response += ","
                        if box.owner is not None:
                            response += str(box.owner)  # current owner of the box
                        else:
                            response += "-1"  # no one owns this box

                client_socket.send(response.encode("utf-8"))

            # unlock_box message: unlock any locks held by the player
            elif token_name == "Unlock_Box":
                for box in boxes:
                    box.unlock(client_id)

        except ConnectionResetError:
            break

    print(f"[-] Connection closed from {address}")

    # update connected client count
    with connected_count_lock:
        connected_count -= 1
        # when connected client count drops to 0, reset the game (get new word)
        if connected_count == 0:
            max_connected_count = 0
            init_game()

    client_socket.close()


def start_server(host="0.0.0.0", port=5555):
    global stop_running
    global server_socket
    # Server setup on '0.0.0.0' and port 5555
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)

    print(f"[*] Listening on {host}:{port}")

    init_game()

    while not stop_running:
        # for each connected player, launch a thread for communicating with that player
        client_socket, addr = server_socket.accept()
        client_handler = threading.Thread(
            target=handle_client, args=(client_socket, addr)
        )
        client_handler.start()


if __name__ == "__main__":
    try:
        start_server()
    except KeyboardInterrupt:
        print("\nShutting Down Server")
        server_socket.close()
        stop_running = True
        
