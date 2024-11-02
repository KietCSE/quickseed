import threading
import time
import random

MAX_UNCHOKE = 4
AVOID_DEADLOCK = 30
REGULAR_UNCHOKE = 5
OPTIMISTICALLY_UNCHOKE = 15
MAX_CONNECTION = 15
CHECKOP = "HERE AT OPTIMISTICALLY"
mutex = threading.Semaphore(1)
m = threading.Semaphore(0)
INIT_LIST = [100, 200, 300, 400]
class Test:
    def __init__(self):
        self.unchoke = INIT_LIST
        self.connected = {}
        self.interested = {}
    def avoidDeadlock(self):
        while True:
            time.sleep(AVOID_DEADLOCK)
            try:
                mutex.release()
            except Exception as e:
                print(f"OK. No deadlock found")
    
    def reEvaluteTopPeersBody(self):
            print('reevalute')
        # with mutex:
            self.unchoke = []
            # if not len(self.connected):
            #     return
            firstPriority = {}
            for key in self.interested:
                if key in self.connected:
                    firstPriority[key] = self.connected[key]
            lengthOfFirstPriority = len(firstPriority)
            # print(f"\033[1;34m{f"First Priority: {firstPriority}"}\033[0m")
            if lengthOfFirstPriority == MAX_UNCHOKE:
                self.unchoke += list(firstPriority.keys())
            elif lengthOfFirstPriority < MAX_UNCHOKE:
                self.unchoke += list(firstPriority.keys())
                sortedConnected = sorted(self.connected.items(), key = lambda item: item[1], reverse = True)
                # unchoke += [peer[0] for peer in sortedConnected[: MAX_UNCHOKE - lengthOfFirstPriority]]
                for peer, _ in sortedConnected:
                    if peer in self.unchoke:
                        continue
                    self.unchoke.append(peer)
                    if len(self.unchoke) == MAX_UNCHOKE:
                        break
            else:
                sortedFirstPriority = sorted(firstPriority.items(), key = lambda item : item[1], reverse = True)
                self.unchoke = [peer[0] for peer in sortedFirstPriority[: MAX_UNCHOKE]]
            # print(f"\033[1;34m{f"Unchoke: {self.unchoke}"}\033[0m")
            # m.release()
    def reEvaluteTopPeers(self):
        t0 = threading.Thread(target = self.reEvaluteTopPeersBody)
        t0.start()
        t0.join()
        t1 = threading.Thread(target = self.optimisticallyUnchokeBody)
        t1.start()
        t1.join()
        t = threading.Timer(REGULAR_UNCHOKE, self.reEvaluteTopPeersBody)
        count = 0
        while True:
            count += 1
            t.start()
            t.join()
            t = threading.Timer(REGULAR_UNCHOKE, self.reEvaluteTopPeersBody)
            print(count)
            if count % 3 == 0:
                self.optimisticallyUnchokeBody()

    def optimisticallyUnchokeBody(self):
            print('optimistically')
        # with mutex:
            # m.acquire()
            if len(self.connected) > MAX_UNCHOKE:
                # print(f"\033[1;31m{CHECKOP}\033[0m")
                connectedKeys = list(self.connected.keys())
                randomPeer = random.choice(connectedKeys)
                # print(f"\033[1;31m{f"Random Peer: {randomPeer}"}\033[0m")
                while randomPeer in self.unchoke:
                    pass
                self.unchoke.append((randomPeer, 'optimistically'))
                # print(f"\033[1;31m{f"Unchoke: {self.unchoke}"}\033[0m")
    def optimisticallyUnchoke(self):
        t0 = threading.Thread(target = self.optimisticallyUnchokeBody)
        t0.start()
        t0.join()
        t = threading.Timer(OPTIMISTICALLY_UNCHOKE, self.optimisticallyUnchokeBody)
        while True:
            t.start()
            t.join()
            t = threading.Timer(OPTIMISTICALLY_UNCHOKE, self.optimisticallyUnchokeBody)
    def test(self):
            print('test')
            randomLengthOfInterested = random.randint(0, MAX_CONNECTION)
            randomLengthOfConnected = random.randint(1, MAX_CONNECTION)
            interestedKeys = [random.randint(0, MAX_CONNECTION) for _ in range(0, randomLengthOfInterested)]
            connectedKeys = [random.randint(0, MAX_CONNECTION) for _ in range(0, randomLengthOfConnected)]
        # with mutex:
            self.interested = {}
            self.connected = {}
            for key in interestedKeys:
                # self.interested[key] = random.randint(30, 100)
                self.interested[key] = 0
            for key in connectedKeys:
                # self.interested[key] = random.randint(30, 100)
                self.connected[key] = 0
            # print(f"\033[1;32m{f"Interested: {list(self.interested.keys())}"}\033[0m")
            # print(f"\033[1;32m{f"Connected: {list(self.connected.keys())}"}\033[0m")
    def printUnchoke(self):
        while True:
                time.sleep(2)
            # with mutex:
                print(self.unchoke)
    def main(self):
        threading.Thread(target = self.test).start()
        threading.Thread(target = self.reEvaluteTopPeers).start()
        # threading.Thread(target = self.optimisticallyUnchoke).start()
        threading.Thread(target = self.printUnchoke).start()
        # threading.Thread(target = self.avoidDeadlock).start()
        SIMULATE_CHANGE_TIME = random.randint(5, 20)
        SIMULATE_CHANGE_TIME = 1
        t = threading.Timer(SIMULATE_CHANGE_TIME, self.test)
        while True:
            t.start()
            t.join()
            t = threading.Timer(SIMULATE_CHANGE_TIME, self.test)
            SIMULATE_CHANGE_TIME = random.randint(5, 20)
        
test = Test()
test.main()