# coding:utf-8
import threading
import time
import DownLoadFile
import Queue


from tools import Logger


def action(sid,eid):
    log = Logger.Log()
    t=DownLoadFile.SyncPhoneTel()
    #t=test.test()
    log.info('thread %s 开始.' % threading.current_thread().name)
    t.run(sid,eid)

    log.info('thread %s 处理完成.' % threading.current_thread().name)



if __name__ == '__main__':
    rootDir="D:\python\data_process\\tools\download"
    #rootDir="/data0/qiniu/image"
    #line = '/2015-12-16/30fdeb60d4a534da3856ae64daf7750.jpg'
    f=open("test.txt","r")
    line=f.readline()
    downloadFile=DownLoadFile()
    domain='https://image.mujinnong.com/'
    queueLock=threading.Lock()
    workQueue=Queue.Queue()
    queueLock.acquire()
    while line:

        print(domain,line)
        line1=line.replace("\n","")
        workQueue.put(line1)
        line = f.readline()


    f.close()
    queueLock.release()
    i=1
    while i<=50:

        t =threading.Thread(target=downloadFile.getFile,args=(domain, rootDir))
        t.start()
        i=i+1
        time.sleep(1)
    print('over')


