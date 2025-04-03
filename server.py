import socket
import threading
import random

locks = []
the_word = ""
the_points = []
the_fullbox = []

def handle_client(client_socket, address):
    print(f"[+] New connection from {address}")

    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            if not message:
                break

            message = message.split(",")

            if message[0] == "Request_Box":
                if locks[int(message[1])] == 0:
                    locks[int(message[1])] = address
                    response = f"1"
                    client_socket.send(response.encode('utf-8'))
                else:
                    response = f"0"
                    client_socket.send(response.encode('utf-8'))

            elif message[0] == "Guess":
                locks[int(message[2])] = 0
                if message[1] == the_word[int(message[2])]:
                    response = f"1"
                    the_points[int(message[2])] = 1
                    client_socket.send(response.encode('utf-8'))
                else:
                    response = f"0"
                    client_socket.send(response.encode('utf-8'))

            elif message[0] == "Request_Update":
                response = f""
                for i in the_points:
                    response = response + str(i)
                client_socket.send(response.encode('utf-8'))

            elif message[0] == "get_word":
                print("send")
                response = f"{the_word}"
                client_socket.send(response.encode('utf-8'))

            elif message[0] == "unlock_box":
                for i in range(len(the_word)):
                    if locks[i] == address:
                        locks[i] = 0
                        
            # print(the_points)

            # response = f"Echo: {message}"
            # client_socket.send(response.encode('utf-8'))
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

    the_word = random.choice(words)
    locks = [0] * (len(the_word) + 1)
    the_points = [0] * len(the_word)
    the_fullbox = [0] * len(the_word)

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen(5)
    print(f"[*] Listening on {host}:{port}")

    while True:
        client_socket, addr = server.accept()
        client_handler = threading.Thread(target=handle_client, args=(client_socket, addr))
        client_handler.start()


if __name__ == "__main__":
    start_server()
