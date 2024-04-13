from socket  import *
import time
import threading
import pickle
import random
import string



# In the Code bellow connection is established  and random username is genreated 

HOST = 'localhost'
PORT = 5000

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
        print("\n New Message :  " , pickle.loads(data) , " \n")
      except:
        a=4

def messageSender():
   
   global connected

   # sending username to the server after openning socket 

   msg = {}
   msg['user'] = username
   msg['type'] = 'onOpenning'
   s.send(pickle.dumps(msg))

   while connected:
       
    #   numberOfOtion = input('Select the Number of an Option :  \n 1- Get Online List  \n 2- Send Message  \n 3- Send Broadcast \n 4- Quit  \n \n \n')
      optionCommand = input('Enter Command  \n \n \n')

      
      if(optionCommand =="@Quit"):
         msg = {}


         msg['user'] = username
         msg['type'] = 'quit'
         s.send(pickle.dumps(dict(msg)))
         s.close()
         connected = False
      elif(optionCommand =="@All"):
         
         # Broadcasting Messages 
         
         message = input('Enter Message :  \n')
         msg = {}
         msg['sender'] = username
         msg['message'] = message
         msg['type'] = 'ALL'
         s.send(pickle.dumps(msg))

      elif(optionCommand =="@List"):
         msg = {}
         msg['type'] = 'List'
         s.send(pickle.dumps(msg))
      elif(optionCommand =="@Chat"):
         
         # Send chat One To One Message
          
         userReceiver = input('Enter Target  Client ID  :\n')
          
         message = input('Enter Message :  \n')
         msg = {}
         msg['sender'] = username
         msg['target'] = userReceiver
         msg['message'] = message
         msg['type'] = 'SERVER'
         s.send(pickle.dumps(msg))

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

