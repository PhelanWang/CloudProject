import os
import re

captured = False


def get_captured():
    global captured
    return captured


def set_captured(true_or_false):
    global captured
    captured = true_or_false


def isPathExist(path):
    isExist=os.path.exists(path)
    if not isExist:
        try:
            os.mkdir(path)
            print("create dir %s success!" % path)
        except Exception,e:
            print("mkdir %s error: " % path+str(e))
            return
    else:
        print("dir %s already exist!" % path)


def isEnd(fp):
    filepointer = fp
    string = filepointer.read()
    if string == '':
        return True
    else:
        return False


def processPack():
    import os
    print os.getcwd()
    try:
        isPathExist(os.getcwd() + "/sec_network/packlog")
        myFile = os.getcwd() + "/sec_network/packlog/originalpackudp"
        os.popen('tshark -i any -R "udp.port==8001" -c 3000 -V > %s' % (myFile))
        f = open(myFile, "r")
        if isEnd(f):
            print("scratch no packages")
            f.close()
            set_captured(False)
            exit()
        f.seek(0,0)
        f2 = open(os.getcwd() + "/sec_network/packlog/filterpackudp", "wr+")
        pattern1 = re.compile(r'Data\s*\(\s*\d*\s*bytes\s*\)')
        patten2 = re.compile(r'\s*Data:\s*\w*')
        patten3 = re.compile(r'\s*Hypertext\s*Transfer\s*Protocol')
        patten4 = re.compile(r'\s*Frame\s*\d*')
        while True:
            string = f.readline()
            if string == '':
                if isEnd(f):
                    break
                continue

            if patten3.match(string):
                while True:
                    string = f.readline()
                    if string == '':
                        if isEnd(f):
                            break
                        continue
                    if patten4.match(string):
                        break
                    f2.writelines(string)

            if pattern1.match(string):
                while True:
                    string = f.readline()
                    if string == '':
                        if isEnd(f):
                            break
                        continue
                    if patten2.match(string):
                        break
                    f2.writelines(string)

        f2.close()
        f.close()
        print("processPack successful!")
        return True
    except Exception,e:
        print("processPack error: "+str(e))


def stringMatch(matchArray,myFile=os.getcwd()+"/set_network/packlog/filterpackudp"):
    try:
        string = ''
        for s in matchArray:
            string += "\s*.*%s.*\s*|"%(str(s))
        string = string[:-1]
        pattern = re.compile(string)
        f = open(myFile, "rb")
        if isEnd(f):
            print("scratch no packages")
            f.close()
            exit()
        f.seek(0,0)
        while True:
            readbuff = ''
            readbuff = f.read()
            if readbuff == '':
                break
            if pattern.search(readbuff):
                print("string match successful!")
                return True
        print("string match failed!")
        f.close()
        return False
    except Exception,e:
        print("stringMatch error: "+str(e))

def getfilterpackupd():
    import os
    myFile = os.getcwd() + "/sec_network/packlog/filterpackudp"
    string = ''
    f=open(myFile,"rb")
    if isEnd(f):
        f.close()
        exit()
    f.seek(0,0)
    while True:
        readbuff = ''
        readbuff = f.read()
        if readbuff == '':
            break
        else:
            string = string + readbuff
    f.close()
    return string


def capture(s):
    import os
    array = ['message']
    processPack()
    if stringMatch(array, os.getcwd() + "/sec_network/packlog/filterpackudp"):
        set_captured(True)
        print "the data is captured"
    else:
        set_captured(False)
        print "the data is cannot captured"
        
        
        
        