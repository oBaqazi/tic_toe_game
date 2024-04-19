from socket  import *
import time
import threading
import pickle
import random
import string





HOST = 'localhost'
PORT = 4000

s = socket(AF_INET, SOCK_STREAM)
s.connect((HOST, PORT)) 

connected = True  

username = ''.join(random.choice(
                        string.ascii_lowercase
                        + string.ascii_uppercase
                        + string.digits)
                   for i in range(8))



# This functionm will be called in diffrent thread to receive incoming messages 

def messageReceiver():
   


   while connected:
       
      try: 
        data = s.recv(1024)     # receive the response
        print("\n New Message :  " , data , " \n")
      except Exception as e:
        print(e)

def messageSender():
   
   global connected

   # sending username to the server after openning socket 

   msg = {}
   msg['user'] = username
   msg['type'] = 'onOpenning'
   s.send(pickle.dumps(msg))

   while connected:
      time.sleep(2)
   

def alivePing():
   
   while connected:
     
     time.sleep(5)
     msg = {}
     msg['user'] = username
     msg['type'] = 'alive'
     s.send(pickle.dumps(msg))
   

def main():
   
   
   
   print("Hello User : ", username)

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



