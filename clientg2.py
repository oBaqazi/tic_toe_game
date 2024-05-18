import socket
import time
import threading
import pickle
import sys

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
              if "message" in message:
                print(f"\n{message['message']}\n")

              elif "gameUpdate" == message["type"]:
                game["id"] = message['data']["id"]
                game["player1"] = message['data']["player1"]
                game["player2"] = message['data']["player2"]
                game["board"] = message['data']["board"]
                game["is_running"] = message['data']['is_running']
                game['whos_turn'] = message['data']['whos_turn']
                game["message"] = message['data']['message']
                game['status'] = message["data"]["status"]
                if message['data']['status'] not in ["ready", "playing", "ended"]:
                   print(game["message"])
                else:
                  print("")
                  print(game["board"])
                  print(game["message"])

              elif "onlineUsers" == message["type"]:
                print(f"\n{message['data']}\n")

              elif "Welcome to Tic Tac Toe!" == message["data"]:
                print("Welcome to Tic Tac Toe!")
                # Handle name input
                msg = {}
                msg['sender'] = name
                msg['type'] = 'connection'
                client_socket.send(pickle.dumps(msg))

              elif "Play Request" == message["data"]:
                print()
                
              elif "wins" == message["data"] or "tie" == message["data"]:
                # End of game
                break
            except Exception as e:
                print("Exception: " + e.__str__())


                
        except (ConnectionResetError, socket.error):
            print("Server disconnected.")
            break

    client_socket.close()

def alivePing():
   
   while True:
     time.sleep(10)
     pingMsg = {}
     pingMsg['sender'] = name
     pingMsg['type'] = 'ping'
     client_socket.send(pickle.dumps(pingMsg))


def messageSender():
    
    global letter
    sendMsg = {}
    sendMsg['sender'] = name
    global game
    game = {}
    while True:
       time.sleep(1)
       command = input('Enter your Command : ')
       
       if command == "onlineUsers":
           sendMsg['type'] = command           
       elif command == "Enter a Game":
          sendMsg['type'] = command
          opponent = input('Enter your opponenet : ')
          sendMsg["recipient"] = opponent
       elif command == "play":
          if game is {}:
             print("Game not started yet, please use 'Enter a Game' command to start a game.")
             sendMsg["type"] = ""
          else:
            sendMsg["gameId"] = game["id"]
            sendMsg["letter"] = letter
            sendMsg['type'] = command
            sendMsg["recipient"] = ""
            client_socket.send(pickle.dumps(sendMsg))
            
            while game["status"] != "ready":
                  pass
            
            while game['is_running']:
              if game["status"] == "ended":
                 break
              sendMsg["type"] = "playing"
              if game["whos_turn"] == name:   
                move = input("Enter your move row,col : ")
                move = move.split(",")
                x = move[0]
                y = move[1]
                sendMsg["x"] = x
                sendMsg["y"] = y
                client_socket.send(pickle.dumps(sendMsg))
              time.sleep(2)
              
       elif command == "quit" or command == "exit":
          print("exiting...")
          sendMsg["type"] = "exit"
          client_socket.send(pickle.dumps(sendMsg))
          client_socket.close()
          sys.exit(0)
       else:
          print("Invalid input")
          sendMsg["type"] = ''

       client_socket.send(pickle.dumps(sendMsg))

if __name__ == '__main__':

    clientThread = threading.Thread(target=client_program)
    clientThread.start()
    threadAlive = threading.Thread(target=alivePing )
    threadAlive.start()
    senderThread = threading.Thread(target=messageSender)
    senderThread.start()
    
