from socket  import *
import time
import threading
import pickle
import random
import redis
import os

channel = "gameXO"
HOST = '0.0.0.0'
PORT = int(os.environ['serverPort'])
# PORT = 5000


r = redis.from_url('redis://redis:6379')

# r = redis.from_url('redis://127.0.0.1:6379')

serverId = random.randint(1, 900)

SIZE = 1024
FORMAT = "UTF-8"
DISCONNECT_MSG = "close"


def handle_client(conn, addr):
    print(f"[NEW CONNECTION] {addr} connected.")


    connected = True
    connectedUser = ""

    while connected:
        
        try:
          msg = conn.recv(SIZE)
        except:
           print("connection is lost : ", connectedUser)
           connected = False
           conn.close()
           

def sendBroadcastMsg(msg):
   
   r.publish(channel ,pickle.dumps(msg) )

def listenToMsg():

   pubsub = r.pubsub()
   pubsub.subscribe(channel)
   for message in pubsub.listen():
        type = message['type']
        if type != "message":
           print(message)
        else:
           msg = pickle.loads(message['data'])
           if int(msg['sender']) != int(serverId):
              print(msg)
        
           

def aliveChecker():
   
   while True:
      time.sleep(3)
              
    
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

    threadAlive = threading.Thread(target=aliveChecker)
    threadAlive.start()



if __name__ == "__main__":
  print(r.ping())
  r.set("1","Ali")

  listner = threading.Thread(target=listenToMsg)
  listner.start()

  time.sleep(3)

  msg = {}

  msg['sender'] = serverId
  msg['data'] = "Hello"


  sendBroadcastMsg(msg)
  main()