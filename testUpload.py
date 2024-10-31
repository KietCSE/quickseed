import threading
import time
import random

MAX_UNCHOKE = 4
REGULAR_UNCHOKE = 1
OPTIMISTICALLY_UNCHOKE = 2
MAX_CONNECTION = 10

mutex = threading.Lock()
def reEvaluteTopPeersBody(interested: dict, connected: dict, unchoke: list):
    firstPriority = {}
    for key in interested:
        if key in connected:
            # print(f'here: {key}')
            firstPriority[key] = connected[key]
    lengthOfFirstPriority = len(firstPriority)
    mutex.acquire()
    if lengthOfFirstPriority == MAX_UNCHOKE:
        unchoke += list(firstPriority.keys())
    elif lengthOfFirstPriority < MAX_UNCHOKE:
        unchoke += list(firstPriority.keys())
        sortedConnected = sorted(connected.items(), key = lambda item: item[1], reverse = True)
        unchoke += [peer[0] for peer in sortedConnected[: MAX_UNCHOKE - lengthOfFirstPriority]]
    else:
        sortedFirstPriority = sorted(firstPriority.items(), key = lambda item : item[1], reverse = True)
        unchoke = [peer[0] for peer in sortedConnected[: MAX_UNCHOKE]]
    mutex.release()
def reEvaluteTopPeers(interested: dict, connected: dict, unchoke: list):
    t = threading.Timer(REGULAR_UNCHOKE, reEvaluteTopPeersBody, args=(interested, connected, unchoke))
    while True:
        t.start()
        t.join()
        t = threading.Timer(REGULAR_UNCHOKE, reEvaluteTopPeersBody, args=(interested, connected, unchoke))

def optimisticallyUnchokeBody(interested: dict, connected: dict, unchoke: list):
    if len(unchoke) != MAX_UNCHOKE and len(connected) > 0:
        connectedKeys = list(connected.keys())
        randomPeer = random.choice(connectedKeys)
        while randomPeer in unchoke:
            randomPeer = random.choice(connectedKeys)
        mutex.acquire()
        unchoke.append((randomPeer, 'optimistically'))
        mutex.release()
def optimisticallyUnchoke(interested: dict, connected: dict, unchoke: list):
    t = threading.Timer(OPTIMISTICALLY_UNCHOKE, optimisticallyUnchokeBody, args=(interested, connected, unchoke))
    while True:
        t.start()
        t.join()
        t = threading.Timer(OPTIMISTICALLY_UNCHOKE, optimisticallyUnchokeBody)
        
for _ in range(10):
    print(f"time: {_}",)
    randomLengthOfInterested = random.randint(0, MAX_CONNECTION)
    randomLengthOfConnected = random.randint(0, MAX_CONNECTION)
    interestedKeys = [random.randint(0, MAX_CONNECTION) for _ in range(0, randomLengthOfInterested)]
    connectedKeys = [random.randint(0, MAX_CONNECTION) for _ in range(0, randomLengthOfConnected)]
    interested = {}
    connected = {}
    unchoke = []
    for key in interestedKeys:
        interested[key] = random.randint(30, 100)
    for key in connectedKeys:
        connected[key] = random.randint(30, 100)
    print(f'interested: {interested}')
    print(f'connected:, {connected}')
    if _ == 0:
        threading.Thread(target=reEvaluteTopPeers, args=(interested, connected, unchoke)).start()
        threading.Thread(target=optimisticallyUnchoke, args=(interested, connected, unchoke)).start()
    print('unchoke:', unchoke)
    time.sleep(1)