from socket  import *
import time
import threading
import pickle
import random
import redis
import os



connectedList = []
channel = "gameXO"
HOST = '0.0.0.0'
PORT = int(os.environ['serverPort'])
# PORT = 4000


r = redis.from_url('redis://redis:6379')

# r = redis.from_url('redis://127.0.0.1:6379')

serverId = random.randint(1, 900)

SIZE = 1024
FORMAT = "UTF-8"
DISCONNECT_MSG = "close"


class TicTacToe:
    def __init__(self,gameId,player1,player2):
        self.gameId = gameId
        self.board = [[' ' for _ in range(3)] for _ in range(3)]
        self.current_winner = None
        self.player1 = player1
        self.player2 = player2

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
    





def handle_client(conn, addr):
    print(f"[NEW CONNECTION] {addr} connected.")

    firstMsg = {}
    firstMsg["data"]= "Welcome to Tic Tac Toe!"
    firstMsg["type"]= "connection"
    conn.send(pickle.dumps(firstMsg))

  

    connected = True
    username = ""
    connectedUser = {}
    
    while connected:        
        try:
          msg = conn.recv(SIZE)
          msg = pickle.loads(msg)
          print("Receveic :")
          print(msg)

          if msg["type"] == "ping":
             connectedUser["ttl"] = time.time()
             r.set(f"user:{username}",serverId,3)

          elif msg["type"] == "onlineUsers":
             sendMsg = {}
             keys = []
             for key in r.scan_iter("*user:*"):
                key = key.decode("utf-8")
                userId = key.replace("user:", '')
                keys.append(userId)
             sendMsg["type"] = "onlineUsers"
             sendMsg["data"] = keys
             conn.send(pickle.dumps(sendMsg))

          elif msg["type"] == "Enter a Game":
             gameId = random.randrange(1, 10000)
             game = TicTacToe(gameId,connectedUser["username"], msg["recipient"])
             r.set(f"game:{gameId}",pickle.dumps(game))
             game = pickle.loads(r.get(f"game:{gameId}"))
             publishMsg = {}
             tmpGame = {}
             tmpGame["id"] = game.gameId
             tmpGame["player1"] = game.player1
             tmpGame["player2"] = game.player2
             tmpGame["board"] = game.board
             publishMsg["data"] = tmpGame
             publishMsg["recipient"] = msg["recipient"]
             publishMsg["type"] = "gameUpdate"
             msgPublisher(publishMsg)

          elif msg["type"] == "play":
             gameId = msg["gameId"]
             game = pickle.loads(r.get(f"game:{gameId}"))
             game.board[int(msg["x"])][int(msg["y"])] = msg["letter"]
             r.set(f"game:{game.gameId}",pickle.dumps(game))
             game = pickle.loads(r.get(f"game:{game.gameId}"))
             publishMsg = {}
             tmpGame = {}
             tmpGame["id"] = game.gameId
             tmpGame["player1"] = game.player1
             tmpGame["player2"] = game.player2
             tmpGame["board"] = game.board
             publishMsg["data"] = tmpGame
             publishMsg["recipient"] = msg["recipient"]
             publishMsg["type"] = "gameUpdate"
             msgPublisher(publishMsg)
               
          elif msg["type"] == "connection":
             
             username = msg["sender"]
             connectedUser['username'] = username
             connectedUser['conn'] = conn
             connectedUser['addr'] = addr
             connectedUser["ttl"] = time.time()
             connectedList.append(connectedUser)
             r.set(f"user:{username}",serverId,3)
             

             
           
        except Exception as e:
           print("exception in connection  : ", e)
           connected = False
           conn.close()
        
        
           
def msgPublisher(msg):
   r.publish(channel ,pickle.dumps(msg) )


def msgSubscriber():

   pubsub = r.pubsub()
   pubsub.subscribe(channel)
   for message in pubsub.listen():
        type = message['type']
        if type != "message":
           print("")
        else:
           msg = pickle.loads(message['data'])
           if msg["type"] == "gameUpdate":
             play1 = msg["data"]["player1"]
             play2 = msg["data"]["player2"]
             for user in connectedList:
               if user["username"] == play1 or user["username"] == play2:
                 conn = user["conn"]
                 conn.send(pickle.dumps(msg))
           else:
             for user in connectedList:
               if user["username"] == msg["recipient"]:
                 conn = user["conn"]
                 conn.send(pickle.dumps(msg))
           print(msg)




def pingCheck():
   
   while True:
     
     time.sleep(3)
     for i in range(len(connectedList)):
        ttl = connectedList[i]["ttl"]

        if (time.time() - ttl) > 4:
           connectedList.pop(i)

      
           
           
        
               
def main():
  
  tmp = "server is startred Id: " + str(serverId) + "   Port: " + str(PORT)
  print(tmp)
  
  s = socket(AF_INET, SOCK_STREAM)
  s.bind((HOST, PORT))
  s.listen(5)
  while True:
    (conn, addr) = s.accept()  # returns new socket and addr. client 
    thread = threading.Thread(target=handle_client, args=(conn, addr))
    thread.start()

if __name__ == "__main__":


  listner = threading.Thread(target=msgSubscriber)
  listner.start()

  pingChecker = threading.Thread(target=pingCheck)
  pingChecker.start()


  time.sleep(3)

  msg = {}

  msg['sender'] = serverId
  msg['data'] = "Hello"
  msg['type'] = "test"


  msgPublisher(msg)
  main()