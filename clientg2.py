import socket
import time
import threading
import pickle


name = None
client_socket = None

name = input("Enter your name: ")

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

                
              elif "Input move" == message["data"]:
                # Handle move input
                move = input("Enter your move (row,col): ")
                client_socket.send(move.encode("utf-8"))

              elif message["data"] == "gameUpdate":
                print(message)
                
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
    
    sendMsg = {}
    sendMsg['sender'] = name
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
          move = input('Enter a move : ')
          
      
       
       client_socket.send(pickle.dumps(sendMsg))

if __name__ == '__main__':

    clientThread = threading.Thread(target=client_program)
    clientThread.start()
    threadAlive = threading.Thread(target=alivePing )
    threadAlive.start()
    senderThread = threading.Thread(target=messageSender)
    senderThread.start()
    
