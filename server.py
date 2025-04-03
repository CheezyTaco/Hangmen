import socket
import threading
import random

locks = []          # locks for each character box
the_word = ""       # the random word chosen for the game
the_points = []     # keep track of which characters are guessed correctly
the_fullbox = []    #

def handle_client(client_socket, address):
    print(f"[+] New connection from {address}")

    while True:
        try:
            # Receive a message from a player
            message = client_socket.recv(1024).decode('utf-8')
            if not message:
                break

            # split the message
            message = message.split(",")

            # Request box message (message[1]: the ith box)
            if message[0] == "Request_Box":
                # If the lock at the ith box is available, set the lock as the player's address
                if locks[int(message[1])] == 0:
                    locks[int(message[1])] = address
                    response = f"1"
                    client_socket.send(response.encode('utf-8'))
                # The lock is not available
                else:
                    response = f"0"
                    client_socket.send(response.encode('utf-8'))

            # Guess message (message[1]: the character guess, message[2]: the ith box)
            elif message[0] == "Guess":
                # Unlocks the lock for the ith box
                locks[int(message[2])] = 0

                # If the guess is correct, update 'the_points' by setting the ith box = 1
                if message[1] == the_word[int(message[2])]:
                    response = f"1"
                    the_points[int(message[2])] = 1
                    client_socket.send(response.encode('utf-8'))
                # The guess is incorrect
                else:
                    response = f"0"
                    client_socket.send(response.encode('utf-8'))

            # Request_Update message: send 'the_points' to let player know which characters are correctly guessed
            elif message[0] == "Request_Update":
                response = f""
                for i in the_points:
                    response = response + str(i)
                client_socket.send(response.encode('utf-8'))

            # get_word message: send the randomly chosen word for the player. (the word must be same for all players)
            elif message[0] == "get_word":
                print("send")
                response = f"{the_word}"
                client_socket.send(response.encode('utf-8'))

            # unlock_box message: unlock any locks held by the player
            elif message[0] == "unlock_box":
                for i in range(len(the_word)):
                    if locks[i] == address:
                        locks[i] = 0

        except ConnectionResetError:
            break

    print(f"[-] Connection closed from {address}")
    client_socket.close()


def start_server(host='0.0.0.0', port=5555):
    words = ["banana", "cherry", "apple"]

    global locks
    global the_word
    global the_points
    global the_fullbox

    the_word = random.choice(words)     # choose the random word
    locks = [0] * (len(the_word) + 1)   # generate len(the_word) amount of locks
    the_points = [0] * len(the_word)    # generate len(the_word) amount of points value
    the_fullbox = [0] * len(the_word)   #

    # Server setup on '0.0.0.0' and port 5555
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen(5)

    print(f"[*] Listening on {host}:{port}")

    while True:
        # for each connected player, launch a thread for communicating with that player
        client_socket, addr = server.accept()
        client_handler = threading.Thread(target=handle_client, args=(client_socket, addr))
        client_handler.start()


if __name__ == "__main__":
    start_server()
