import socket
import time
import threading
import pickle


name = None
client_socket = None
game = {}

name = input("Enter your name: ")
letter = input("Enter your letter: ")

def client_program():
    global client_socket
    global name

    host = "127.0.0.1"
    port = 4000
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))

    while True:
        try:

            message = client_socket.recv(1024)
            try:
             
              message = pickle.loads(message)
              if "gameUpdate" == message["type"]:
                game["id"] = message['data']["id"]
                game["player1"] = message['data']["player1"]
                game["player2"] = message['data']["player2"]
                game["board"] = message['data']["board"]
                print(f"\n{message['data']}\n")

              if "onlineUsers" == message["type"]:
                print(f"\n{message['data']}\n")

              if "Welcome to Tic Tac Toe!" == message["data"]:
                print("Welcome to Tic Tac Toe!")
                # Handle name input
                msg = {}
                msg['sender'] = name
                msg['type'] = 'connection'
                client_socket.send(pickle.dumps(msg))

              if "Play Request" == message["data"]:
                print()
                
              elif "wins" == message["data"] or "tie" == message["data"]:
                # End of game
                break
            except Exception as e:
                print(e)


                
        except (ConnectionResetError, socket.error):
            print("Server disconnected.")
            break

    client_socket.close()

def alivePing():
   
   while True:
      
     time.sleep(1)
     pingMsg = {}
     pingMsg['sender'] = name
     pingMsg['type'] = 'ping'
     client_socket.send(pickle.dumps(pingMsg))


def messageSender():
    
    global letter
    sendMsg = {}
    sendMsg['sender'] = name
    global game
    while True:
       time.sleep(2)
       

       command = input('Enter your Command : ')

       if command == "onlineUsers":
           sendMsg['type'] = command           
       elif command == "Enter a Game":
          sendMsg['type'] = command
          opponent = input('Enter your oppoenet : ')
          sendMsg["recipient"] = opponent
       elif command == "play":
          move = input("Enter your move row,col : ")
          move = move.split(",")
          x = move[0]
          y = move[1]
          sendMsg["x"] = x
          sendMsg["y"] = y
          sendMsg["gameId"] = game["id"]
          sendMsg["letter"] = letter
          sendMsg['type'] = command
          sendMsg["recipient"] = ""

       client_socket.send(pickle.dumps(sendMsg))

if __name__ == '__main__':

    clientThread = threading.Thread(target=client_program)
    clientThread.start()
    threadAlive = threading.Thread(target=alivePing )
    threadAlive.start()
    senderThread = threading.Thread(target=messageSender)
    senderThread.start()
    
