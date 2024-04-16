# encoding=utf-8
import os,sys
import urllib
import Queue
import threading
import time
sys.path.append('../')
from etc import logs
flag=0
class DownLoadFile():
    def __init__(self):
        self.log=logs.Log()
    def callbackfunc(self,blocknum, blocksize, totalsize):
        '''回调函数
        @blocknum: 已经下载的数据块
        @blocksize: 数据块的大小
        @totalsize: 远程文件的大小
        '''
        percent = 100.0 * blocknum * blocksize / totalsize
        if percent > 100:
            percent = 100
        print "%.2f%%"% percent



    def getFile(self,domain,rootDir):
        global flag
        while not flag:

            queueLock.acquire()
            if not workQueue.empty():
                self.url=workQueue.get()
                queueLock.release()
            else:
                flag=1
                queueLock.release()

            #print(threading.current_thread().name ,self.url)

            self.local = self.url.split('/')
            self.fileName=self.local[-1]
            self.listDir=self.local[0:-1]

            self.dirs=''
            if self.listDir!=[""] and self.listDir!=[]:
                #print("listDir",listDir)
                for i in self.listDir:
                    if i !="" and i!=".":
                        i=i+'/'
                        self.dirs=self.dirs+i
                #print('dirs',dirs)

                if not os.path.exists(self.dirs):
                    try:
                        os.makedirs(self.dirs)
                    except Exception as E:
                        print("create dir failed : ", E)
                        self.log.writeLog.error(E)
            #os.chdir(rootDir+self.dirs)


            #self.fileName=rootDir+self.dirs+self.fileName
            self.urls=domain+self.url

            try:
                urllib.urlretrieve(self.urls, self.url)
                self.fileName=""
            except Exception as E:
                self.log.writeLog.error(self.urls)

            self.log.writeLog.info(threading.current_thread().name + 'download finish'+"   "+ self.urls )
        self.log.writeLog.info('thread %s 处理完成.' % threading.current_thread().name)


if __name__ == '__main__':
    #rootDir="D:\python\data_process\\tools\download\\"
    rootDir="/data0/qiniu/jiufu_nongdai_fenli/"
    #line = '/2015-12-16/30fdeb60d4a534da3856ae64daf7750.jpg'
    f=open("jiufu_nongdai_fenli.txt","r")
    line=f.readline()
    downloadFile=DownLoadFile()
    domain='https://image.mujinnong.com/'
    queueLock=threading.Lock()
    workQueue=Queue.Queue()
    queueLock.acquire()
    os.chdir(rootDir)
    while line:


        line1=line.replace("\n","")
        workQueue.put(line1)
        line = f.readline()
    print('put over')

    f.close()
    queueLock.release()
    i=1
    #downloadFile.getFile(domain,rootDir)

    while i<=100:

        t =threading.Thread(target=downloadFile.getFile,args=(domain, rootDir))
        t.start()

        i=i+1

        print(i)
    print('over')



