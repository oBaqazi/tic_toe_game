from socket  import *
import time
import threading
import pickle
import random
import redis


 
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


    connected = True
    connectedUser = ""

    while connected:
        
        try:
          msg = conn.recv(SIZE)
        except:
           print("connection is lost : ", connectedUser)
           connected = False
           conn.close()
           lock.acquire()
           clientList.pop(msg['user'])
           clientTTL.pop(msg['user'])
           onelineUser.remove(msg['user'])
           msg = "Current Online Users  :  " , onelineUser
           sendBroadcastMsg(msg)
           lock.release()

           break
        msg = pickle.loads(msg)
        msg = dict(msg)
        
        if msg['type'] == 'onOpenning':
           print("User : ",msg['user'] , " is Connected")
           connectedUser = msg['user']
           lock.acquire()
           clientList[msg['user']] = conn
           clientTTL[msg['user']] = time.time()
           onelineUser.append(msg['user'])
           msg = "Current Online Users  :  " , onelineUser
           sendBroadcastMsg(msg)
           lock.release()
           
        elif msg['type'] == 'quit':
           connected = False

           lock.acquire()
           clientList.pop(msg['user'])
           onelineUser.remove(msg['user'])
           msg = "Current Online Users  :  " , onelineUser
           sendBroadcastMsg(msg)
           lock.release()

           conn.close()

        elif msg['type'] == 'SERVER':
           print("Sending To : ", msg['target'])
           
           userConnection = ""

           try:
              userConnection = clientList[msg['target']]
              userConnection.send(pickle.dumps(msg))
           except:
              conn.send(pickle.dumps("User Is offline , try later"))

        elif msg['type'] == 'ALL':
           print("Sending Broadcast Message ")
           msg['type'] = 'BROADCAST'
           sendBroadcastMsg(msg)           

        elif msg['type'] == 'alive':
           clientTTL[msg['user']] = time.time()

        elif msg['type'] == 'List':
           lock.acquire()
           conn.send(pickle.dumps(onelineUser))
           lock.release()


    conn.close()



def sendBroadcastMsg(messageToPublish):
   
   for i in clientList.keys():
      userConnection = clientList[i]
      userConnection.send(pickle.dumps(messageToPublish))  



def aliveChecker():
   
   while True:
     
     indexList = []
     time.sleep(5)
     lock.acquire()
     for i in clientTTL.keys():
        ttl = clientTTL[i]

        if (time.time() - ttl) > 6:
           print(" No alive ping from : ", i)
           indexList.append(i)
           onelineUser.remove(i)
           msg = "Current Online Users  :  " , onelineUser
           sendBroadcastMsg(msg)

     for i in indexList:
        clientTTL.pop(i)

     lock.release()
              
    



         
   

def main():
  
  print("App is startred")
  timeToLive = 10
  HOST = '0.0.0.0'
  PORT = 5000
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
  r = redis.from_url('redis://redis:6379')
  print(r.ping())
  main()