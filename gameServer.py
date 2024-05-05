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
# PORT = int(os.environ['serverPort'])
PORT = 5000


# r = redis.from_url('redis://redis:6379')

r = redis.from_url('redis://127.0.0.1:6379')

serverId = random.randint(1, 900)

SIZE = 1024
FORMAT = "UTF-8"
DISCONNECT_MSG = "close"


def handle_client(conn, addr):
    print(f"[NEW CONNECTION] {addr} connected.")

    connected = True
    username = ""
    connectedUser = {}
    
    while connected:        
        try:
          msg = conn.recv(SIZE)
          msg = pickle.loads(msg)

          if msg["type"] == "ping":
             print(f"{addr} connection is a live.")
             connectedUser["ttl"] = time.time()
             r.set(f"user:{username}",serverId,3)

          elif msg["type"] == "onlineUsers":
             keys = []
             for key in r.scan_iter("*user:*"):
                key = key.decode("utf-8")
                userId = key.replace("user:", '')
                keys.append(userId)
             conn.send(pickle.dumps(keys))

          elif msg["type"] == "gameUpdate":
             msgPublisher(msg)
                

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

def msgPublisher(msg):
   r.publish(channel ,pickle.dumps(msg) )


def msgSubscriber():

   pubsub = r.pubsub()
   pubsub.subscribe(channel)
   for message in pubsub.listen():
        type = message['type']
        if type != "message":
           print(message)
        else:
           msg = pickle.loads(message['data'])
           for user in connectedList:
              if user["username"] == msg["recipient"]:
                 conn = user["conn"]
                 conn.send(pickle.dumps(msg))
           print(msg)
         #   if int(msg['sender']) != int(serverId):
         #      print(msg)


def pingCheck():
   
   while True:
     
     time.sleep(3)
     for i in range(len(connectedList)):
        ttl = connectedList[i]["ttl"]

        if (time.time() - ttl) > 3:
           connectedList.pop(i)
     print(connectedList)

      
           
           
        
               
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
  print(r.ping())


  listner = threading.Thread(target=msgSubscriber)
  listner.start()

  pingChecker = threading.Thread(target=pingCheck)
  pingChecker.start()


  time.sleep(3)

  msg = {}

  msg['sender'] = serverId
  msg['data'] = "Hello"


  msgPublisher(msg)
  main()