# uncompyle6 version 3.2.3
# Python bytecode 2.7 (62211)
# Decompiled from: Python 2.7.5 (default, Jul 13 2018, 13:06:57) 
# [GCC 4.8.5 20150623 (Red Hat 4.8.5-28)]
# Embedded file name: /root/git/ovirt/engine_ta/encryption/enginecheck.py
# Compiled at: 2016-05-23 10:39:39
__author__ = 'pushpin'
import os, sys

class enginecheck(object):

    def __init__(self, ip):
        self.ip = ip
        self.port_file = '.port_info%s' % self.ip
        self.info_file = '.info%s' % self.ip

    def str_search(self, fileopen, search_for=None):
        result_list = []
        if search_for == None:
            return result_list
        for line in fileopen:
            if line.find(search_for) != -1:
                line = line.strip('\n')
                result_list.append(line)

        fileopen.seek(0)
        return result_list

    def port_scan(self):
        ip = self.ip
        scan_port = 'nmap %s' % ip
        http_search = 'http'
        port_list = []
        port_file = self.port_file
        os.system(scan_port + '> ./%s' % port_file)
        try:
            file_io = open('./%s' % port_file)
            port_list = self.str_search(file_io, http_search)
        except Exception:
            pass
        finally:
            file_io.close()
            os.system('rm ./%s' % port_file)

        return port_list

    def port_get(self, port_list):
        portAndpro = []
        for eachline in port_list:
            port_and_pro = eachline.split()
            # if port_and_pro[2] == 'http' or port_and_pro[2] == 'https':
            if port_and_pro[2] == 'https':
                port = int(port_and_pro[0].split('/')[0])
                portAndpro.append([port, port_and_pro[2]])

        return portAndpro

    def openssl_generate(self, ip, port):
        ip = self.ip
        info_file = self.info_file
        openssl_command = 'openssl s_client -connect %s:%d' % (ip, port)
        os.system(openssl_command + ' > ./%s' % info_file)
        return os.path.abspath('%s' % info_file)

    def cipher_verificate(self, file_io):
        search_for = 'Cipher    :'
        cainfo = self.str_search(file_io, search_for)
        return cainfo

    def get_certificate(self, file_io):
        import re
        certificate = re.findall(r'-----BEGIN CERTIFICATE-----.+?-----END CERTIFICATE-----', file_io.read(), re.S)
        file_io.seek(0)
        return certificate

    def signing_digest(self, file_io):
        search_for = 'Peer signing digest'
        signing_digest = self.str_search(file_io, search_for)
        return signing_digest

    def master_key(self, file_io):
        search_for = 'Master-Key'
        master_key = self.str_search(file_io, search_for)
        return master_key

    def protocol_check(self, file_io):
        search_for = 'Protocol'
        proinfo = self.str_search(file_io, search_for)
        return proinfo

    def tools_version(self):
        files = self.info_file
        fileio = open(files, 'a+')
        temp = ''
        for lines in fileio:
            temp += lines

        os.system('openssl version > %s' % files)
        ag = open(files, 'a')
        fileio.write(temp)
        fileio.close()

    def cipher_bits(self, fileio):
        search_for = 'Server public key'
        bits_info = self.str_search(fileio, search_for)
        return bits_info

    def engine_check(self):
        ip = self.ip
        listabc = self.port_scan()
        port = self.port_get(listabc)
        conclusion = []
        for item in port:
            tempfile = self.openssl_generate(ip, item[0])
            try:
                file_io = open(tempfile)
                cipher_info = self.cipher_verificate(file_io)
                protocol_info = self.protocol_check(file_io)
                bits_info = self.cipher_bits(file_io)
                certificate_info = self.get_certificate(file_io)
                master_key = self.master_key(file_io)
                digist_info = self.signing_digest(file_io)

                conclusion.append([item[0], item[1], cipher_info, protocol_info, bits_info, certificate_info, master_key, digist_info])
            except Exception:
                pass
            finally:
                file_io.close()

        return conclusion