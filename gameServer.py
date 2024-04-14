from socket  import *
import time
import threading
import pickle
import random
import redis


channel = "gameXO"
HOST = '0.0.0.0'
PORT = 5000
r = redis.from_url('redis://redis:6379')

 
def getOnlineList():
  return ""

def addUserToOnlineList():
  return ""

def removeUserFromOnlineList():
  return ""

SIZE = 1024
FORMAT = "UTF-8"
DISCONNECT_MSG = "close"

clientList = {}
clientTTL = {}
onelineUser = []

lock = threading.Lock()



def handle_client(conn, addr):
    print(f"[NEW CONNECTION] {addr} connected.")

    conn.close()



def sendBroadcastMsg(messageToPublish):
   
   r.publish(channel , messageToPublish)
   print(r.get("1"))

def listenToMsg():

   pubsub = r.pubsub()
   pubsub.subscribe(channel)
   for message in pubsub.listen():
        print(message)


def aliveChecker():
   
   while True:
      time.sleep(3)
              
    
def main():
  
  print("App is startred")
  
  s = socket(AF_INET, SOCK_STREAM)
  s.bind((HOST, PORT))
  s.listen(1)
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
  msg = "Hi everyone"

  sendBroadcastMsg(msg)
  main()