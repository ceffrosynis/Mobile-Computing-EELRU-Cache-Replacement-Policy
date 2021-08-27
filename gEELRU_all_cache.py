import random
import math
import sys
import statistics

hitRatio = {}

class GeneralPacket():
    def __init__(self, packetID):
        self.packetID = packetID

class Transmitter():
    def __init__(self, transPolicy):
        self.tP = transPolicy
        
    def getNextPacket(self):
        randomNumber = random.random()
        for i in range(len(self.tP)):
            if randomNumber <= self.tP[i]:
                return GeneralPacket(i)
        
class LRU():
    def __init__(self, cacheSize):
        self.cache = []
        self.maxCacheSize = cacheSize
    
    def getPacket(self, packetID):
        for i in range(len(self.cache)):
            if packetID == self.cache[i].packetID:
                tmp =  self.cache.pop(i)
                self.cache.insert(0, tmp)
                return tmp
        return None
    
    def updateCache(self, packet):        
        if len(self.cache) == self.maxCacheSize:
            self.cache.pop()
        self.cache.insert(0, packet)

class EELRU():
    def __init__(self,
                 earlyEvictionPoint,
                 lateEvictionPoint,
                 cacheSize,
                 globalIdx = 0):
        self.e = earlyEvictionPoint
        self.l = lateEvictionPoint
        self.M = cacheSize
        self.eCounter = 0
        self.totalCounter = 0
        self.idx = globalIdx
        self.earlyRatio = (self.M - self.e)/(self.l - self.e)
        self.cache = []
        self.meta = {}
    
    def getPacket(self, packetID):
        if packetID in self.meta:
            if self.meta[packetID] < 0:
                return None
            for i in range(len(self.cache)):
                if packetID == self.cache[i].packetID:
                    tmp = self.cache.pop(i)
                    self.cache.insert(0, tmp)
                    if i >= self.e:
                        self.totalCounter += 1
                        if  i <= self.M:#equal to M
                            self.eCounter += 1                   
                    return tmp
                
        else:
            return None        
    
    def updateCache(self, packet):    
        if len(self.cache) < self.M:
            self.meta[packet.packetID] = 1
            self.cache.insert(0, packet)
            return     
        
        lruIdx = -1
                
        for i in range(len(self.cache)-1, 0, -1):
            if self.meta[self.cache[i].packetID] == 1:
                lruIdx = i
                break
        
        holeIdx = 0
        if packet.packetID in self.meta:
            holeIdx = -self.meta[packet.packetID]

        self.meta[packet.packetID] = 1
        
        if lruIdx == self.l and holeIdx == 0:
            del self.meta[self.cache[self.l].packetID]
            self.cache.pop(self.l)
            self.cache.insert(0, packet)
            return          
        
        rmIdx = lruIdx if self.totalCounter * self.earlyRatio <= self.eCounter else self.e
        tmpID = self.cache[rmIdx].packetID            
        self.meta[tmpID] = -rmIdx
        self.cache[rmIdx] = GeneralPacket(tmpID)                             
           
        if holeIdx != 0:
            for i in range(holeIdx, len(self.cache)):
                if self.cache[i].packetID == packet.packetID:
                    holeIdx = i
                    break
            self.cache.pop(holeIdx)
        elif len(self.cache) == self.l:
            tmpID = self.cache.pop().packetID
            del self.meta[tmpID]              
        self.cache.insert(0, packet)


class GeneralEELRU():
    def __init__(self,
                 earlyEvictionPoints,
                 lateEvictionPoints,
                 cacheSize
                 ):
        assert len(earlyEvictionPoints) == len(lateEvictionPoints)
        self.e = earlyEvictionPoints
        self.l = lateEvictionPoints
        self.M = cacheSize
        self.eCounter = []
        self.totalCounter = []
        self.earlyRatio = []
        for i in range(len(self.e)):
            self.eCounter.append(0)
            self.totalCounter.append(0)
            self.earlyRatio.append((self.M-self.e[i])/(self.l[i]-self.e[i]))
            assert self.earlyRatio[i] > 0
        self.cache = []
        self.meta = {}
        
    def getPacket(self, packetID):
        if packetID in self.meta:
            if self.meta[packetID] < 0:
                return None
            for i in range(len(self.cache)):
                if packetID == self.cache[i].packetID:
                    tmp = self.cache.pop(i)
                    self.cache.insert(0, tmp)
                    
                    if i >= self.e[0]:
                        for j in range(len(self.e)-1, 0, -1):                                
                            if i <= self.M:
                                if i >= self.e[j]:
                                    self.eCounter[j] += 1                          
                                    self.totalCounter[j] += 1
                            elif i <= self.l[j]:
                                self.totalCounter[j] += 1                                                                 
                    return tmp
                
        else:
            return None

    def updateCache(self, packet):
        if len(self.cache) < self.M:
            self.meta[packet.packetID] = 1
            self.cache.insert(0, packet)
            return
        
        lruIdx = -1
                        
        for i in range(len(self.cache)-1, 0, -1):
            if self.meta[self.cache[i].packetID] == 1:
                lruIdx = i
                break
        
        holeIdx = 0
        if packet.packetID in self.meta:
            holeIdx = -self.meta[packet.packetID]

        self.meta[packet.packetID] = 1        
        
        maxIdx = 0
        benefit =  self.totalCounter[0]*self.earlyRatio[0]-self.eCounter[0]
                
        for i in range(1, len(self.eCounter)):
            tmp = self.totalCounter[i]*self.earlyRatio[i]-self.eCounter[i]
            if (benefit < tmp):
                maxIdx = i
                benefit = tmp
                
        if holeIdx != 0:
            for i in range(holeIdx, len(self.cache)):
                if self.cache[i].packetID == packet.packetID:
                    holeIdx = i
                    break       
        
        lmaxVal = self.meta[self.l[maxIdx]] if self.l[maxIdx] in self.meta else -1
        
        if (benefit <= 0 or lruIdx > self.l[maxIdx] or
            (lmaxVal > 0 and (holeIdx == 0 or
             holeIdx > self.l[maxIdx]))):
            tmpID = self.cache[lruIdx].packetID
            self.meta[tmpID] = -lruIdx
            self.cache[lruIdx] = GeneralPacket(tmpID)
            
            if holeIdx != 0:
                self.cache.pop(holeIdx)
            elif len(self.cache) == self.l[0]:
                tmpID = self.cache.pop().packetID
                del self.meta[tmpID]
            self.cache.insert(0, packet)
            assert not len(self.cache) > self.l[0]
            return 
        
        eID = self.cache[self.e[maxIdx]].packetID
        self.meta[eID] = -self.e[maxIdx]
        self.cache[self.e[maxIdx]] = GeneralPacket(eID)
        
        if holeIdx != 0:
            self.cache.pop(holeIdx)
        elif len(self.cache) == self.l[0]:
            tmpID = self.cache.pop().packetID
            del self.meta[tmpID]
        assert not len(self.cache) > self.l[0]
        self.cache.insert(0, packet)
        
              
def createEvictionRegionsOLD(M, lRegionLength, eRegionLength, lMax, eMin):
    ePoints = []
    lpoints = []
    point = M - eRegionLength
    
    while point >= eMin:
        ePoints.insert(0, point)
        point -= eRegionLength
    
    assert len(ePoints) > 0
    
    point = M + lRegionLength
    
    while point <= lMax:
        lpoints.insert(0, point)
        point += lRegionLength
    assert len(lpoints) > 0
    return ePoints, lpoints

def createPacketDistribution(packetNumber, theta=1):
    transPolicy = []
    w = 0
    for i in range(packetNumber):
        w += math.pow(1/(i+1), theta)
        transPolicy.append(w)
    for i in range(packetNumber):
        transPolicy[i] = transPolicy[i]/w
    return transPolicy

class Receiver():
    def __init__(self, transPolicy, cachePolicy, cachePolicyArgs):
        global hitRatio
        hitRatio["hits"] =  0
        hitRatio["misses"] = 0
        self.prob = transPolicy
        self.cache = cachePolicy(*cachePolicyArgs)
        self.packetNotInCache = True
        self.expectedPacketID = self.getNextPacketID()
    
    def getNextPacketID(self):
        randomNumber = random.random()
        for i in range(len(self.prob)):
            if randomNumber <= self.prob[i]:
                return i
    
    def receive(self, packet):
        global hitRatio
        if self.packetNotInCache:
            if self.expectedPacketID == packet.packetID:
                self.cache.updateCache(packet)
                self.packetNotInCache = False
                self.expectedPacketID = self.getNextPacketID()
        else:
            if self.cache.getPacket(self.expectedPacketID) is None:
                hitRatio["misses"] += 1
                self.packetNotInCache = True                                  
            else:
                hitRatio["hits"] += 1
                self.expectedPacketID = self.getNextPacketID()


def createEvictionRegions(M, nRegions, lMax, eMin):
    ePoints = []
    lPoints = []
    eRegionLength = (M-eMin)/nRegions
    lRegionLength = (lMax-M)/nRegions
    
    point = M - eRegionLength
    
    while point >= eMin:
        ePoints.insert(0, point)
        point -= eRegionLength
    
    assert len(ePoints) > 0
    
    point = M + lRegionLength
    
    while point <= lMax:
        lPoints.insert(0, point)
        point += lRegionLength
    assert len(lPoints) == len(ePoints)
    return ePoints, lPoints
    

def GeneralEELRUTester():
    global hitRatio
    total = 1000
    packetNo = [512, 768, 1024]
    cacheSize = [64, 128, 256]
    seeds = [902, 830, 166, 93, 782]
    e = {64:[32], 128:[32,64], 256:[32]}
    l = {64:[96], 128:[160,192], 256:[288,320,384]}
    regionNumber = {64:[4,8],128:[4,8], 256:[4,8,16]}
    
    print("Starting...")
    stats = {}
    for pNumber in packetNo:
        transPolicy = createPacketDistribution(pNumber)
        stats[pNumber] = {}
        for cSize in cacheSize:
            stats[pNumber][cSize] = {}
            for earlyPoint in e[cSize]:
                for latePoint in l[cSize]:
                    for rNum  in regionNumber[cSize]:
                        ePoints, lPoints = createEvictionRegions(cSize, rNum, latePoint, earlyPoint)
                        ratios = []
                        for seed in seeds:                    
                            random.seed(seed)    
                            tx = Transmitter(transPolicy)
                            rx = Receiver(transPolicy, GeneralEELRU, (ePoints, lPoints, cSize))
                            
                            while (hitRatio['hits']+hitRatio['misses'] < total):
                                packet = tx.getNextPacket()
                                rx.receive(packet)                                                            
                            ratios.append(100*hitRatio['hits']/(hitRatio['hits'] + hitRatio['misses']))                            
                        stats[pNumber][cSize][(earlyPoint, latePoint, rNum)] = [statistics.mean(ratios), statistics.stdev(ratios)]

        print("+++++++_{}_+++++++++".format(cSize))
        print(stats)
        print("++++++++++++++++")
    print(stats)
    return        
        
def LRUTester():
    global hitRatio
    total = 1000
    packetNo = [512, 768, 1024]
    cacheSize = [64, 128, 256]
    seeds = [902, 830, 166, 93, 782]

    stats = {}
    for pNumber in packetNo:
        transPolicy = createPacketDistribution(pNumber)
        stats[pNumber] = {}
        for cSize in cacheSize:
            ratios = []
            for seed in seeds:                    
                random.seed(seed)    
                tx = Transmitter(transPolicy)
                rx = Receiver(transPolicy, LRU, (cSize,))
                ct = 0
                
                while (hitRatio['hits']+hitRatio['misses'] < total):
                    ct += 1
                    packet = tx.getNextPacket()
                    rx.receive(packet)
                ratios.append(100*hitRatio['hits']/(hitRatio['hits'] + hitRatio['misses']))
            stats[pNumber][cSize] = [statistics.mean(ratios), statistics.stdev(ratios)]
    
    print(stats)
    return  

def EELRUTester():
    global hitRatio
    total = 1000
    packetNo = [512, 768, 1024]
    cacheSize = [64, 128, 256]
    seeds = [902, 830, 166, 93, 782]
    e = {256:[128, 100, 40], 128:[100, 40], 64:[40]}
    l = [128, 100, 64]
    print("Starting...")
    stats = {}
    for pNumber in packetNo:
        transPolicy = createPacketDistribution(pNumber)
        stats[pNumber] = {}
        for cSize in cacheSize:
            stats[pNumber][cSize] = {}
            for earlyPoint in e[cSize]:
                for latePoint in l:
                    ratios = []
                    for seed in seeds:                    
                        random.seed(seed)    
                        tx = Transmitter(transPolicy)
                        rx = Receiver(transPolicy, EELRU, (earlyPoint, latePoint+cSize, cSize))
                        
                        while (hitRatio['hits']+hitRatio['misses'] < total):
                            packet = tx.getNextPacket()
                            rx.receive(packet)                            
                        ratios.append(100*hitRatio['hits']/(hitRatio['hits'] + hitRatio['misses']))
                    stats[pNumber][cSize][(earlyPoint, latePoint+cSize)] = [statistics.mean(ratios), statistics.stdev(ratios)]
        print("+++++++++++_{}_++++++++".format(cSize))
        print(stats)
        print("+++++++++++++++++++++++")
    print(stats)
    return  

def main():
    GeneralEELRUTester()
    #EELRUTester()
    #LRUTester()
    
if __name__ == "__main__":    
    main()






















    
    



    
