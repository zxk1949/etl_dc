#!/usr/bin/env python

import dns.resolver
import threading
import os


iplist = []

appdomain = "dsadmin.qa.huohua.cn"


def get_iplist(domain="mysqls1.qa.huohua.cn"):
    num=0




    try:
        my_resolver = dns.resolver.Resolver()
        my_resolver.nameservers = ['172.16.208.8']
        A=my_resolver.query(domain,"A")

    except Exception as e:

        print ("dns resolver error:" + str(e))

        return

    for i in A.response.answer:


        for j in i.items:


            if j.rdtype == 1:
                num=1
                # iplist.append(j.address)

    return num

def main():
    sum=0
    for i in range(10000):
        n=get_iplist(appdomain)
        sum=sum+n
        if sum%100==0:
            print ("{1}已处理{0}".format(sum,threading.current_thread().name))

if __name__ == "__main__":
    s=1
    while s<=50:

        t =threading.Thread(target=main)
        t.start()

        s=s+1

        print(s)