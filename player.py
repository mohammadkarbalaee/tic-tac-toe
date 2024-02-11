# Import necessary libraries
import pygame
import socket
import time
import threading
import random
# Create a socket object
s = socket.socket()
# Get the server IP address from the user
host = "127.0.0.1"
port = 9999
# Define player constants and colors
playerOne = 1
playerOneColor = (random.randint(0,255), random.randint(0,255), random.randint(0,255))
playerTwo = 2
playerTwoColor = (random.randint(0,255), random.randint(0,255), random.randint(0,255))
bottommessage = ""
message = "Waiting for peer"
currentPlayer = 0
xy = (-1, -1)
allow = 0  # Allow handling mouse events
matrix = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
# Function to create worker threads
def CreateThread(target):
    t = threading.Thread(target=target)  # Argument - target function
    t.daemon = True
    t.start()
# Initialize pygame
pygame.init()
# Randomly set the width and height of the game window
width = random.randint(600, 800)
height = random.randint(550, 750)
screen = pygame.display.set_mode((width, height))
# Set the title of the window
pygame.display.set_caption("Game Board")
# Set the window icon
icon = pygame.image.load("tictactoe.png")
pygame.display.set_icon(icon)
# Set fonts, background color, and title/subtitle/line colors
bigfont = pygame.font.Font('freesansbold.ttf', random.randint(64, 80))
smallfont = pygame.font.Font('freesansbold.ttf', random.randint(32, 40))
backgroundColor = (random.randint(0,255), random.randint(0,255), random.randint(0,255))
titleColor = (random.randint(0,255), random.randint(0,255), random.randint(0,255))
subtitleColor = (random.randint(0,255), random.randint(0,255), random.randint(0,255))
lineColor = (random.randint(0,255), random.randint(0,255), random.randint(0,255))
# Function to build and display the game screen
def buildScreen(bottommessage, string, playerColor=subtitleColor):
    screen.fill(backgroundColor)
    if "One" in string or "1" in string:
        playerColor = playerOneColor
    elif "Two" in string or "2" in string:
        playerColor = playerTwoColor
    # Draw vertical lines
    pygame.draw.line(screen, lineColor, (250-2, 150), (250-2, 450), 4)
    pygame.draw.line(screen, lineColor, (350-2, 150), (350-2, 450), 4)
    # Draw horizontal lines
    pygame.draw.line(screen, lineColor, (150, 250-2), (450, 250-2), 4)
    pygame.draw.line(screen, lineColor, (150, 350-2), (450, 350-2), 4)
    title = bigfont.render("TIC TAC TOE", True, titleColor)
    screen.blit(title, (110, 0))
    subtitle = smallfont.render(str.upper(string), True, playerColor)
    screen.blit(subtitle, (150, 70))
    centerMessage(bottommessage, playerColor)
# Function to display a centered message at the bottom of the screen
def centerMessage(message, color=titleColor):
    pos = (100, 480)
    if "One" in message or "1" in message:
        color = playerOneColor
    elif "Two" in message or "2" in message:
        color = playerTwoColor
    messageRendered = smallfont.render(message, True, color)
    screen.blit(messageRendered, pos)
# Function to display the current matrix on the screen
def printCurrent(current, pos, color):
    currentRendered = bigfont.render(str.upper(current), True, color)
    screen.blit(currentRendered, pos)
# Function to print the entire matrix on the screen
def printMatrix(matrix):
    for i in range(3):
        # When row increases, y changes
        y = int((i + 1.75) * 100)
        for j in range(3):
            # When col increases, x changes
            x = int((j + 1.75) * 100)
            current = " "
            color = titleColor
            if matrix[i][j] == playerOne:
                current = "X"
                color = playerOneColor
            elif matrix[i][j] == playerTwo:
                current = "O"
                color = playerTwoColor
            printCurrent(current, (x, y), color)
# Function to validate user input for matrix coordinates
def ValidateInput(x, y):
    if x > 3 or y > 3:
        print("\nOut of bound! Enter again...\n")
        return False
    elif matrix[x][y] != 0:
        print("\nAlready entered! Try again...\n")
        return False
    return True
# Function to handle mouse events and update matrix
def handleMouseEvent(pos):
    x = pos[0]
    y = pos[1]
    global currentPlayer
    global xy
    if(x < 150 or x > 450 or y < 150 or y > 450):
        xy = (-1, -1)
    else:
        # When x increases, column changes
        col = int(x/100 - 1.5)
        # When y increases, row changes
        row = int(y/100 - 1.5)
        print("({}, {})".format(row, col))
        if ValidateInput(row, col):
            matrix[row][col] = currentPlayer
            xy = (row, col)
# Function to start the player and connect to the server
def StartPlayer():
    global currentPlayer
    global bottommessage
    try:
        s.connect((host, port))
        print("Connected to:", host, ":", port)
        recvData = s.recv(2048 * 10)
        bottommessage = recvData.decode()
        if "1" in bottommessage:
            currentPlayer = 1
        else:
            currentPlayer = 2
        StartGame()
        s.close()
    except socket.error as e:
        print("Socket connection error:", e)
# Function to start the game loop
def StartGame():
    running = True
    global message
    global matrix
    global bottommessage
    CreateThread(AcceptMessage)
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONUP:
                pos = pygame.mouse.get_pos()
                if allow:
                    handleMouseEvent(pos)
        if message == "":
            break
        buildScreen(bottommessage, message)
        printMatrix(matrix)
        pygame.display.update()
# Function to continuously receive messages from the server
def AcceptMessage():
    global matrix
    global message
    global bottommessage
    global allow
    global xy
    while True:
        try:
            recvData = s.recv(2048 * 10)
            recvDataDecode = recvData.decode()
            buildScreen(bottommessage, recvDataDecode)
            if recvDataDecode == "Input":
                failed = 1
                allow = 1
                xy = (-1, -1)
                while failed:
                    try:
                        if xy != (-1, -1):
                            coordinates = str(xy[0]) + "," + str(xy[1])
                            s.send(coordinates.encode())
                            failed = 0
                            allow = 0
                    except:
                        print("Error occurred....Try again")
            elif recvDataDecode == "Error":
                print("Error occurred! Try again..")
            elif recvDataDecode == "Matrix":
                print(recvDataDecode)
                matrixRecv = s.recv(2048 * 100)
                matrixRecvDecoded = matrixRecv.decode("utf-8")
                matrix = eval(matrixRecvDecoded)
            elif recvDataDecode == "Over":
                messageRecv = s.recv(2048 * 100)
                messageRecvDecoded = messageRecv.decode("utf-8")
                bottommessage = messageRecvDecoded
                message = "~~~Game Over~~~"
                break
            else:
                message = recvDataDecode
        except KeyboardInterrupt:
            print("\nKeyboard Interrupt")
            time.sleep(1)
            break
        except:
            print("Error occurred")
            break
# Start the player
StartPlayer()