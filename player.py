import pygame
import socket
import time
import threading

class TicTacToeClient:
    def __init__(self):
        self.s = socket.socket()
        self.host = "127.0.0.1"
        self.port = 9999
        self.playerOne = 1
        self.playerOneColor = (255, 0, 0)
        self.playerTwo = 2
        self.playerTwoColor = (0, 0, 255)
        self.bottomMsg = ""
        self.msg = "Waiting for peer"
        self.currentPlayer = 0
        self.xy = (-1, -1)
        self.allow = 0  # allow handling mouse events
        self.matrix = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]

    def create_thread(self, target):
        t = threading.Thread(target=target)
        t.daemon = True
        t.start()

    def init_game(self):
        pygame.init()
        width = 600
        height = 550
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Tic Tac Toe")
        icon = pygame.image.load("tictactoe.png")
        pygame.display.set_icon(icon)
        self.bigfont = pygame.font.Font('freesansbold.ttf', 64)
        self.smallfont = pygame.font.Font('freesansbold.ttf', 32)
        self.backgroundColor = (255, 255, 255)
        self.titleColor = (0, 0, 0)
        self.subtitleColor = (128, 0, 255)
        self.lineColor = (0, 0, 0)

    def build_screen(self):
        self.screen.fill(self.backgroundColor)
        player_color = self.subtitleColor
        if "One" in self.msg or "1" in self.msg:
            player_color = self.playerOneColor
        elif "Two" in self.msg or "2" in self.msg:
            player_color = self.playerTwoColor
        pygame.draw.line(self.screen, self.lineColor, (250 - 2, 150), (250 - 2, 450), 4)
        pygame.draw.line(self.screen, self.lineColor, (350 - 2, 150), (350 - 2, 450), 4)
        pygame.draw.line(self.screen, self.lineColor, (150, 250 - 2), (450, 250 - 2), 4)
        pygame.draw.line(self.screen, self.lineColor, (150, 350 - 2), (450, 350 - 2), 4)
        title = self.bigfont.render("TIC TAC TOE", True, self.titleColor)
        self.screen.blit(title, (110, 0))
        subtitle = self.smallfont.render(str.upper(self.msg), True, player_color)
        self.screen.blit(subtitle, (150, 70))
        self.center_message(self.bottomMsg, player_color)

    def center_message(self, msg, color):
        pos = (100, 480)
        msg_rendered = self.smallfont.render(msg, True, color)
        self.screen.blit(msg_rendered, pos)

    def print_current(self, current, pos, color):
        current_rendered = self.bigfont.render(str.upper(current), True, color)
        self.screen.blit(current_rendered, pos)

    def print_matrix(self):
        for i in range(3):
            y = int((i + 1.75) * 100)
            for j in range(3):
                x = int((j + 1.75) * 100)
                current = " "
                color = self.titleColor
                if self.matrix[i][j] == self.playerOne:
                    current = "X"
                    color = self.playerOneColor
                elif self.matrix[i][j] == self.playerTwo:
                    current = "O"
                    color = self.playerTwoColor
                self.print_current(current, (x, y), color)

    def validate_input(self, x, y):
        if x > 3 or y > 3:
            print("\nOut of bound! Enter again...\n")
            return False
        elif self.matrix[x][y] != 0:
            print("\nAlready entered! Try again...\n")
            return False
        return True

    def handle_mouse_event(self, pos):
        x = pos[0]
        y = pos[1]
        if x < 150 or x > 450 or y < 150 or y > 450:
            self.xy = (-1, -1)
        else:
            col = int(x / 100 - 1.5)
            row = int(y / 100 - 1.5)
            print("({}, {})".format(row, col))
            if self.validate_input(row, col):
                self.matrix[row][col] = self.currentPlayer
                self.xy = (row, col)

    def start_player(self):
        try:
            self.s.connect((self.host, self.port))
            print("Connected to:", self.host, ":", self.port)
            recv_data = self.s.recv(2048 * 10)
            self.bottomMsg = recv_data.decode()
            if "1" in self.bottomMsg:
                self.currentPlayer = 1
            else:
                self.currentPlayer = 2
            self.init_game()
            self.create_thread(self.accept_msg)
            self.start_game()
            self.s.close()
        except socket.error as e:
            print("Socket connection error:", e)

    def start_game(self):
        running = True
        self.build_screen()
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.MOUSEBUTTONUP:
                    pos = pygame.mouse.get_pos()
                    if self.allow:
                        self.handle_mouse_event(pos)
            if self.msg == "":
                break
            self.build_screen()
            self.print_matrix()
            pygame.display.update()

    def accept_msg(self):
        while True:
            try:
                recv_data = self.s.recv(2048 * 10)
                recv_data_decode = recv_data.decode()
                self.build_screen()
                if recv_data_decode == "Input":
                    self.allow = 1
                    self.xy = (-1, -1)
                    while self.xy == (-1, -1):
                        time.sleep(0.1)  # Wait for valid input
                    coordinates = str(self.xy[0]) + "," + str(self.xy[1])
                    self.s.send(coordinates.encode())
                    self.allow = 0
                elif recv_data_decode == "Error":
                    print("Error occurred! Try again..")
                elif recv_data_decode == "Matrix":
                    matrix_recv = self.s.recv(2048 * 100)
                    matrix_recv_decoded = matrix_recv.decode("utf-8")
                    self.matrix = eval(matrix_recv_decoded)
                elif recv_data_decode == "Over":
                    msg_recv = self.s.recv(2048 * 100)
                    self.bottomMsg = msg_recv.decode("utf-8")
                    self.msg = "~~~Game Over~~~"
                    break
                else:
                    self.msg = recv_data_decode
            except KeyboardInterrupt:
                print("\nKeyboard Interrupt")
                time.sleep(1)
                break
            except Exception as e:
                print("Error occurred:", e)
                break

if __name__ == "__main__":
    client = TicTacToeClient()
    client.start_player()
