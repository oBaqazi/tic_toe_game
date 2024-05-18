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
    self.whosTurn = player1
    self.winner_player = None

  def print_board(self):
    board_str = "    0   1   2\n"
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
            self.winner_player = self.whosTurn
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
    
  def is_running(self):
    return not self.is_full() and self.current_winner == None
    
  def next_turn(self):
    if self.whosTurn == self.player1:
      self.whosTurn = self.player2
    else:
      self.whosTurn = self.player1
    

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
             r.set(f"user:{username}",serverId,55)

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
             keys = []
             for key in r.scan_iter("*user:*"):
                key = key.decode("utf-8")
                userId = key.replace("user:", '')
                keys.append(userId)
             if msg['recipient'] in keys:
              gameId = random.randrange(1, 10000)
              game = TicTacToe(gameId,connectedUser["username"], msg["recipient"])
              r.set(f"game:{gameId}",pickle.dumps(game))
              r.set(f"{connectedUser['username']}", pickle.dumps(game))
              game = pickle.loads(r.get(f"game:{gameId}"))
              publishMsg = {}
              tmpGame = {}
              tmpGame["id"] = game.gameId
              tmpGame["player1"] = game.player1
              tmpGame["player2"] = game.player2
              tmpGame["board"] = game.print_board()
              tmpGame['is_running'] = game.is_running()
              tmpGame['whos_turn'] = game.whosTurn
              tmpGame["message"] = f"Game created for {game.player1} vs {game.player2}"
              tmpGame["status"] = "created"
              publishMsg["data"] = tmpGame
              publishMsg["recipient"] = msg["recipient"]
              publishMsg["type"] = "gameUpdate"
              msgPublisher(publishMsg)
             else:
              publishMsg = {}
              publishMsg["message"] = "Player does not exist"
              msgPublisher(publishMsg)
              conn.send(pickle.dumps(publishMsg))


          elif msg["type"] == "play":
            r.set(msg["sender"], "Ready", 50)
            publishMsg = {}
            gameId = msg["gameId"]
            game = pickle.loads(r.get(f"game:{gameId}"))
            p1status = r.get(game.player1)
            p2status = r.get(game.player2)
            if p1status is not None and p1status.decode('utf-8') == "Ready" and p2status is not None and p2status.decode('utf-8') == "Ready":
              msgString = f"Its {game.whosTurn}'s turn"
              tmpGame = {}
              tmpGame["id"] = game.gameId
              tmpGame["player1"] = game.player1
              tmpGame["player2"] = game.player2
              tmpGame["board"] = game.print_board()
              tmpGame['is_running'] = game.is_running()
              tmpGame['whos_turn'] = game.whosTurn
              tmpGame["message"] = msgString
              tmpGame["status"] = "ready"
              publishMsg["data"] = tmpGame
              publishMsg["recipient"] = msg["recipient"]
              publishMsg["type"] = "gameUpdate"
            else:
              tmpGame = {}
              tmpGame["id"] = game.gameId
              tmpGame["player1"] = game.player1
              tmpGame["player2"] = game.player2
              tmpGame["board"] = game.print_board()
              tmpGame['is_running'] = game.is_running()
              tmpGame['whos_turn'] = game.whosTurn
              tmpGame["message"] = "Waiting for both players to start using 'play' command"
              tmpGame["status"] = "awaiting"
              publishMsg["data"] = tmpGame
              publishMsg["recipient"] = msg["recipient"]
              publishMsg["type"] = "gameUpdate"
            msgPublisher(publishMsg)
            
          elif msg["type"] == "playing":
            publishMsg = {}
            gameId = msg["gameId"]
            game = pickle.loads(r.get(f"game:{gameId}"))
            msgString = f"Its {game.whosTurn}'s turn"
            tmpGame = {}
            tmpGame["status"] = "playing"
            result = game.make_move(list([int(msg['x']), int(msg['y'])]), msg['letter'])
            if result == True:
              game.next_turn()
              msgString = f"Its {game.whosTurn}'s turn"
              tmpGame["message"] = msgString
              if game.current_winner is not None:
               tmpGame["message"] = f"{game.winner_player} is the winner"
               tmpGame["status"] = "ended"
              elif game.current_winner is None and game.is_full():
               tmpGame["message"] = f"Game is tie"
               tmpGame["status"] = "ended"
            else:
               if game.current_winner is not None:
                 tmpGame["message"] = f"{game.winner_player} is the winner"
                 tmpGame["status"] = "ended"
               elif game.current_winner is None and game.is_full():
                 tmpGame["message"] = f"Game is tie"
                 tmpGame["status"] = "ended"
               else:
                tmpGame["message"] = "Invalid move, try again "
            # game.board[int(msg["x"])][int(msg["y"])] = msg["letter"]
            r.set(f"game:{game.gameId}",pickle.dumps(game))
            game = pickle.loads(r.get(f"game:{game.gameId}"))
            tmpGame["id"] = game.gameId
            tmpGame["player1"] = game.player1
            tmpGame["player2"] = game.player2
            tmpGame["board"] = game.print_board()
            tmpGame['is_running'] = game.is_running()
            tmpGame['whos_turn'] = game.whosTurn
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
             connectedUser['is_playing'] = False
             connectedList.append(connectedUser)
             r.set(f"user:{username}",serverId,3)
          elif msg['type'] == "exit":
             for i in range(len(connectedList)):
              usr = connectedList[i]["username"]
              if usr == msg["sender"]:
                connectedList.pop(i)
             
           
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
     
     time.sleep(50)
     for i in range(len(connectedList)):
        ttl = connectedList[i]["ttl"]

        if (time.time() - ttl) > 60:
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
