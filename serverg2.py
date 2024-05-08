import socket
import threading

class TicTacToe:
    def __init__(self):
        self.board = [[' ' for _ in range(3)] for _ in range(3)]
        self.current_winner = None
        self.player1 

    def print_board(self):
        board_str = "  0 1 2\n"
        for i, row in enumerate(self.board):
            board_str += f"{i} " + '| ' + ' | '.join(row) + ' |\n'
        return board_str

    def available_moves(self):
        return [(i, j) for i in range(3) for j in range(3) if self.board[i][j] == ' ']

    def make_move(self, position, letter):
        if self.board[position[0]][position[1]] == ' ':
            self.board[position[0]][position[1]] = letter
            if self.winner(position, letter):
                self.current_winner = letter
            return True
        return False

    def winner(self, position, letter):
        row_ind, col_ind = position
        row = all([self.board[row_ind][i] == letter for i in range(3)])
        col = all([self.board[i][col_ind] == letter for i in range(3)])
        diagonal1 = all([self.board[i][i] == letter for i in range(3)]) if row_ind == col_ind else False
        diagonal2 = all([self.board[i][2 - i] == letter for i in range(3)]) if row_ind + col_ind == 2 else False
        return row or col or diagonal1 or diagonal2

    def is_full(self):
        return all([self.board[i][j] != ' ' for i in range(3) for j in range(3)])

class NetworkPlayer:
    def __init__(self, letter, client_socket, name):
        self.letter = letter
        self.client_socket = client_socket
        self.name = name

    def get_move(self, game):
        valid_square = False
        val = None
        while not valid_square:
            try:
                self.client_socket.send("Input move (row,col): ".encode("utf-8"))
                square = self.client_socket.recv(1024).decode("utf-8")
                val = tuple(int(num) for num in square.split(','))
                if val in game.available_moves():
                    valid_square = True
                else:
                    self.client_socket.send("Invalid move. Try again.".encode("utf-8"))
            except (ValueError, ConnectionResetError, socket.error):
                self.client_socket.send("Invalid move. Try again.".encode("utf-8"))
        return val

def play(game, x_player, o_player):
    current_player = x_player
    other_player = o_player
    letter = 'X'

    while game.current_winner is None and not game.is_full():
        try:
            # Send current game board to both players
            board_state = game.print_board().encode("utf-8")
            x_player.client_socket.sendall(board_state)
            o_player.client_socket.sendall(board_state)

            # Request a move from the current player
            prompt = f"It's your turn, {current_player.name} ({letter}).".encode("utf-8")
            current_player.client_socket.sendall(prompt)

            # Get and validate the move
            position = current_player.get_move(game)
            if game.make_move(position, letter):
                if game.current_winner:
                    result = f"{letter} wins the game!\n".encode("utf-8")
                    x_player.client_socket.sendall(result)
                    o_player.client_socket.sendall(result)
                    break
                elif game.is_full():
                    result = "The game is a tie!\n".encode("utf-8")
                    x_player.client_socket.sendall(result)
                    o_player.client_socket.sendall(result)
                    break
                # Switch players for the next turn
                current_player, other_player = other_player, current_player
                letter = 'O' if letter == 'X' else 'X'
            else:
                current_player.client_socket.sendall("Invalid move. Please try again.\n".encode("utf-8"))

        except socket.error as e:
            print(f"Network error: {e}")
            break

    return "Game Over"

def handle_client(conn, addr, player_list):
    print(f"New connection from {addr}")
    conn.send("Welcome to Tic Tac Toe!".encode("utf-8"))
    name = conn.recv(1024).decode("utf-8")
    player_list.append(NetworkPlayer("X" if len(player_list) % 2 == 0 else "O", conn, name))
    if len(player_list) % 2 == 0:
        game = TicTacToe()
        play(game, player_list[-2], player_list[-1])

def server_program():
    host = "127.0.0.1"
    port = 5000

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((host, port))
    server_socket.listen()

    print("Waiting for connections...")

    player_list = []

    try:
        while True:
            conn, addr = server_socket.accept()

            client_handler = threading.Thread(target=handle_client, args=(conn, addr, player_list))
            client_handler.start()

    except KeyboardInterrupt:
        print("Server shutting down...")
        server_socket.close()

if __name__ == '__main__':
    server_program()
