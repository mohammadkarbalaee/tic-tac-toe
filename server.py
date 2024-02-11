import socket
import pickle
import time
import threading

class Game:
    def __init__(self, players):
        self.players = players
        self.matrix = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
        self.playerOne = 1
        self.playerTwo = 2
        self.current_player = self.playerOne
        self.game_over = False

    def start(self):
        self.send_common_msg("Game started!")
        while not self.game_over:
            self.get_input()
            result = self.check_winner()
            if result != 0 or self.is_board_full():
                self.game_over = True
                self.send_common_msg("Over")
                if result == 1:
                    lastmsg = "Player One is the winner!!"
                elif result == 2:
                    lastmsg = "Player Two is the winner!!"
                else:
                    lastmsg = "Draw game!! Try again later!"
                self.send_common_msg(lastmsg)
        time.sleep(10)
        for conn in self.players:
            conn.close()

    def get_input(self):
        current_player = "Player One's Turn" if self.current_player == self.playerOne else "Player Two's Turn"
        self.send_common_msg(current_player)
        try:
            conn = self.players[self.current_player - 1]
            conn.send("Input".encode())
            data = conn.recv(2048 * 10)
            conn.settimeout(20)
            dataDecoded = data.decode().split(",")
            x = int(dataDecoded[0])
            y = int(dataDecoded[1])
            if self.matrix[x][y] == 0:
                self.matrix[x][y] = self.current_player
                self.current_player = self.playerOne if self.current_player == self.playerTwo else self.playerTwo
                self.send_common_msg("Matrix")
                self.send_common_msg(str(self.matrix))
            else:
                conn.send("Error: Cell already occupied".encode())
        except:
            print("Error occurred! Try again..")

    def check_rows(self):
        for i in range(3):
            if self.matrix[i][0] == self.matrix[i][1] == self.matrix[i][2] and self.matrix[i][0] != 0:
                return self.matrix[i][0]
        return 0

    def check_columns(self):
        for i in range(3):
            if self.matrix[0][i] == self.matrix[1][i] == self.matrix[2][i] and self.matrix[0][i] != 0:
                return self.matrix[0][i]
        return 0

    def check_diagonals(self):
        if self.matrix[0][0] == self.matrix[1][1] == self.matrix[2][2] and self.matrix[0][0] != 0:
            return self.matrix[0][0]
        elif self.matrix[0][2] == self.matrix[1][1] == self.matrix[2][0] and self.matrix[0][2] != 0:
            return self.matrix[0][2]
        return 0

    def check_winner(self):
        result = self.check_rows()
        if result == 0:
            result = self.check_columns()
        if result == 0:
            result = self.check_diagonals()
        return result

    def is_board_full(self):
        for row in self.matrix:
            for cell in row:
                if cell == 0:
                    return False
        return True

    def send_common_msg(self, text):
        for conn in self.players:
            conn.send(text.encode())
            time.sleep(1)

class Server:
    def __init__(self):
        self.host = ""
        self.port = 9999
        self.s = socket.socket()
        self.player_threads = []

    def start_server(self):
        try:
            self.s.bind((self.host, self.port))
            print("Tic Tac Toe server started \nBinding to port", self.port)
            self.s.listen()
            while True:
                game_players = []
                for _ in range(2):
                    conn, addr = self.s.accept()
                    print("Player connected from:", addr)
                    game_players.append(conn)
                game = Game(game_players)
                game_thread = threading.Thread(target=game.start)
                game_thread.start()
                self.player_threads.append(game_thread)
                # Join completed game threads
                for thread in self.player_threads:
                    if not thread.is_alive():
                        thread.join()
                        
        except socket.error as e:
            print("Server binding error:", e)
        except KeyboardInterrupt:
            print("\nKeyboard Interrupt")
            exit()
        except Exception as e:
            print("Error occurred:", e)

if __name__ == "__main__":
    server = Server()
    server.start_server()
