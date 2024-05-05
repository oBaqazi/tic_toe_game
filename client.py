from socket  import *
import time
import threading
import pickle

class HumanPlayer:
    def __init__(self, letter):
        self.letter = letter
        self.name = input(f"Enter name for player {letter}: ")

    def get_move(self, game):
        valid_square = False
        val = None
        while not valid_square:
            square = input(f"{self.name}'s turn ({self.letter}). Input move (row,col): ")
            try:
                val = tuple(int(num) for num in square.split(','))
                if val in game.available_moves():
                    valid_square = True
                else:
                    raise ValueError
            except ValueError:
                print('Invalid Move. Try again.')
        return val


HOST = 'localhost'
PORT = 5000
human = None

s = socket(AF_INET, SOCK_STREAM)
s.connect((HOST, PORT)) 

connected = True  





# This functionm will be called in diffrent thread to receive incoming messages 

def messageReceiver():
   
   while connected:
       
      try: 
        data = s.recv(1024)     # receive the response
        print("\n New Message :  " , pickle.loads(data) , " \n")
      except Exception as e:
        print(e)

def messageSender():
   
   global connected
   global human

   msg = {}
   msg['sender'] = human.name
   msg['type'] = 'connection'
   s.send(pickle.dumps(msg))

   while connected:
      time.sleep(2)
      msg = {}
      msg['sender'] = human.name
      command = input('Enter your Command : ')

      if command == "gameUpdate":
         opponent = input('Enter your oppoenet : ')
         msg["recipient"] = opponent
      
      msg['type'] = command


     
      s.send(pickle.dumps(msg))


   

def alivePing():
   global human
   
   while connected:
      
     
     time.sleep(2)
     msg = {}
     msg['username'] = human.name
     msg['type'] = 'ping'
     s.send(pickle.dumps(msg))
   

def main():
   
   global human
   
   letter = input("Enter your Letter : ")
   human = HumanPlayer(letter)
   
   # print("Hello User : ", username)

   # Messages recevier thread 
   threadReceiver = threading.Thread(target=messageReceiver)
   threadReceiver.start()


   # Messages sender thread 
   threadSender = threading.Thread(target=messageSender )
   threadSender.start()

   threadAlive = threading.Thread(target=alivePing )
   threadAlive.start()
   
   threadReceiver.join()
   threadSender.join()
   threadAlive.join()
   
   print("Exit the program") 
   s.close()               # close the connection



if __name__ == "__main__":
  main()



