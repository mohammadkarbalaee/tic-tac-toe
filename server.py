# Import necessary libraries
import socket
import pickle
import time
# Create a socket object
socket = socket.socket()
# Set the host to an empty string and the port to 9999
host = "127.0.0.1"
port = 9999
# Initialize the Tic Tac Toe matrix
matrix = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
# Define player constants
playerOne = 1
playerTwo = 2
# Lists to store player connections and addresses
playerConnections = list()
playerAddresses = list()
# Function to get input from the current player and update the matrix
def GetInput(currentPlayer):
    if currentPlayer == playerOne:
        player = "Turn : 1"
        conn = playerConnections[0]
    else:
        player = "Turn : 2"
        conn = playerConnections[1]
    print(player)
    SendCommonMessage(player)
    try:
        conn.send("Input".encode())
        data = conn.recv(2048 * 10)
        conn.settimeout(20)
        dataDecoded = data.decode().split(",")
        x = int(dataDecoded[0])
        y = int(dataDecoded[1])
        matrix[x][y] = currentPlayer
        SendCommonMessage("Matrix")
        SendCommonMessage(str(matrix))
    except:
        conn.send("Error".encode())
        print("Error occurred! Try again..")
# Function to check for a winner in rows
def CheckRows():
    result = 0
    for i in range(3):
        if matrix[i][0] == matrix[i][1] and matrix[i][1] == matrix[i][2]:
            result = matrix[i][0]
            if result != 0:
                break
    return result
# Function to check for a winner in columns
def CheckColumns():
    result = 0
    for i in range(3):
        if matrix[0][i] == matrix[1][i] and matrix[1][i] == matrix[2][i]:
            result = matrix[0][i]
            if result != 0:
                break
    return result
# Function to check for a winner in diagonals
def CheckDiagonals():
    result = 0
    if matrix[0][0] == matrix[1][1] and matrix[1][1] == matrix[2][2]:
        result = matrix[0][0]
    elif matrix[0][2] == matrix[1][1] and matrix[1][1] == matrix[2][0]:
        result = matrix[0][2]
    return result
# Function to check for a winner in the entire matrix
def CheckWinner():
    result = 0
    result = CheckRows()
    if result == 0:
        result = CheckColumns()
    if result == 0:
        result = CheckDiagonals()
    return result
# Function to start the server and bind to port 9999
def StartServer():
    try:
        socket.bind((host, port))
        print("Tic Tac Toe server started \nBinding to port", port)
        socket.listen(2)
        AcceptPlayers()
    except socket.error as e:
        print("Server binding error:", e)
# Function to accept two players and send them their player numbers
def AcceptPlayers():
    try:
        for i in range(2):
            conn, addr = socket.accept()
            message = "<<< You are : {} >>>".format(i+1)
            conn.send(message.encode())
            playerConnections.append(conn)
            playerAddresses.append(addr)
            print("Player {} - [{}:{}]".format(i+1, addr[0], str(addr[1])))
        StartGame()
        socket.close()
    except socket.error as e:
        print("Player connection error", e)
    except KeyboardInterrupt:
        print("\nKeyboard Interrupt")
        exit()
    except Exception as e:
        print("Error occurred:", e)
# Function to start the game loop
def StartGame():
    result = 0
    i = 0
    while result == 0 and i < 9:
        if i % 2 == 0:
            GetInput(playerOne)
        else:
            GetInput(playerTwo)
        result = CheckWinner()
        i = i + 1   
    SendCommonMessage("Over")
    if result == 1:
        lastmessage = "Player One is the winner!!"
    elif result == 2:
        lastmessage = "Player Two is the winner!!"
    else:
        lastmessage = "Draw game!! Try again later!"
    SendCommonMessage(lastmessage)
    time.sleep(10)
    for conn in playerConnections:
        conn.close()
# Function to send a common message to both players
def SendCommonMessage(text):
    playerConnections[0].send(text.encode())
    playerConnections[1].send(text.encode())
    time.sleep(1)
# Start the server
StartServer()