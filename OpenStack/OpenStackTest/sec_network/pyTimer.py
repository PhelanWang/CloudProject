# coding=utf-8

import threading
import time
# import client as cli
import unsecurity_service as unsecurity


class Pysettimer(threading.Thread):
    '''
    Pysettimer is simulate the C++ settimer ,
    it need  pass funciton pionter into the class ,
    timeout and is_loop could be default , or customized
    '''
    def __init__(self, function, args, timeout=10, is_loop=False):
        threading.Thread.__init__(self)
        self.event=threading.Event()
        # inherent the funciton and args
        self.function=function
        self.args=args      # pass a tuple into the class
        self.timeout=timeout
        self.is_loop=is_loop


    def run(self):
        while not self.event.is_set():
            # self.event.wait(self.timeout) # wait until the time eclipse
            # print self.ident, '  ', self.args[1]
            self.function(self.args)
            if not  self.is_loop:
                self.event.set()
                # self.stop()

    def wait(self):
        self.event.set()



# The following is just for testing
def functest(args):
    print args, time.time()

def fun(args):
    print 'another', time.time()


def main():
    for i in range(2):
        mytime=Pysettimer(functest,('leo' ,))
        mytime.start()

        mytime2=Pysettimer(functest,time.time())
        mytime2.start()
        print("thread-", mytime.ident," is alive: " ,mytime.isAlive())
        # print("thread-", mytime2.ident," is alive: " ,mytime2.isAlive())

        time.sleep(30)                    # append the main thread
        #mytime.stop()
        # mytime2.stop()      # end the timer thread
        print("thread-", mytime.ident," is alive: " ,mytime.isAlive())
        # print("thread-", mytime2.ident," is alive: " ,mytime2.isAlive())
    print 'main over'


if __name__=='__main__':
    main()









