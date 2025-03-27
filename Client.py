# user code for interacting with server
import socket

#establish tcp connection to server
#takes in server ip and port number
#return socket object
def Connect(serverIP, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((serverIP, port))
    return s

#send ready message to server
#takes in socket object and player name
#return true if server responds with 1 (everything is good)
#return false otherwise
def client_Ready(s, pname):
    s.send("Client_Ready," + pname.encode())
    data = s.recv(1024).decode()
    if data == "1":
        return True
    else:
        return False

#check to see if box is available
#takes in socket object and box number
#return true if server responds with 1 (box is available)
#return false otherwise
def Request_Box(s, box_Num):
    s.send("Request_Box," + box_Num.encode())
    data = s.recv(1024).decode()
    if data == "1":
        return True
    else:
        return False
    
#Guess
#takes in socket object, player's guess and box number
#return true if server responds with 1 (guess is correct)
#return false otherwise
def Guess(s, guess, box_Num):
    s.send("Guess," + guess + "," + box_Num.encode())
    data = s.recv(1024).decode()
    if data == "1":
        return True
    else:
        return False
    
#Request update
#takes in socket object
#return server response
def Request_Update(s):
    s.send("Request_Update")
    data = s.recv(1024).decode()
    return data

#Disconnect
#takes in socket object
#no return value, closes socket to server
def Disconnect(s):
    s.close()
    return