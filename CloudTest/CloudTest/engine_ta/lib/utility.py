__author__ = 'Henry'

from time import localtime, strftime
from uuid import uuid1
from threading import Thread
from requests import post, put, get
from json import dumps, loads
from functools import partial
import os, ConfigParser, socket
# Aux API

def now():
    return strftime('%Y-%m-%d %H:%M:%S', localtime())

def uuid():
    return str(uuid1())

def getip():
    '''
    cmd=u'/sbin/ifconfig -a|grep inet|grep -v 127.0.0.1|grep -v inet6|awk \'{print $2}\'|tr -d \"addr:\"'
    ip=os.popen(cmd)
    return str(ip.read()).replace('\n','')
    '''
    # conf=ConfigParser.ConfigParser()
    # conf.read('lib.agent.ctest.conf')
    # return conf.get('network', 'ipaddr')
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ip


# HTTP Request API

def get_url_json(url, timeout=0):
    try:
        do_get = partial(get, url)
        if timeout > 0:
            do_get = partial(do_get, timeout=timeout)
        return do_get().json()
    except:
        return {'code': 'error'}

def get_url_json_with_timeout(url, timeout):
    try:
        return get(url, timeout=timeout).json()
    except:
        return {'code': 'error'}

def put_url(url, payload, timeout=0):
    try:
        headers={'Content-Type': 'application/json'}
        do_put = partial(put, url, data=dumps(payload), headers=headers)
        if timeout > 0:
            do_put = partial(do_put, timeout=timeout)
        return do_put().json()
    except:
        return {'code': 'error'}

def post_url(url, payload, timeout=0):
    try:
        headers={'Content-Type': 'application/json'}
        do_post = partial(post, url, data=dumps(payload), headers=headers)
        if timeout > 0:
            do_post = partial(do_post, timeout=timeout)
        return do_post().json()
    except:
        return {'code': 'error'}

def print_exception(module, exception):
    print '%s module run() exception: %s with %s' % \
          (module, exception.message, exception.args)

# Flask-RESTful resouce API

def add_resource_wrapper(restful_api, base_url):
    def do_add_resource(class_name, api_name, endpoint=None):
        restful_api.add_resource(class_name, "%s/%s" % (base_url, api_name))
    return do_add_resource

def register_api_resources(restful_api, api_map, root_path):
    add_resource = add_resource_wrapper(restful_api, root_path)
    for path, api in api_map.iteritems():
        add_resource(api, path)

# Simple Multi-Thread API

class SimpleThread(Thread):
    def __init__(self, entry_function, *args):
        super(SimpleThread, self).__init__()
        self.entry_function = entry_function
        self.args = args

    def run(self):
        if self.entry_function:
            self.entry_function(self.args[0], self.args[1])

# Global Variable API

def unpack_namespace(base_url, namespace_and_key):
    splitted = str(namespace_and_key).split(':')
    if len(splitted) > 1:
        space_and_type = splitted[0]
        key = splitted[1]
        splitted = space_and_type.split('@')
        if len(splitted) > 1:
            type = splitted[0]
            namespace = splitted[1]
        else:
            type = 'plain'
            namespace = splitted[0]
        url = '%s/switch/global/%s/%s' % (base_url, namespace, key)
    else:
        key_and_type = splitted[0]
        splitted = key_and_type.split('@')
        if len(splitted) > 1:
            type = splitted[0]
            key = splitted[1]
        else:
            type = 'plain'
            key = splitted[0]
        url = '%s/switch/global/%s' % (base_url, key)
    return url, key, type


class GlobalVariable:
    def __init__(self, base_url, name):
        self.url, self.key, self.type = unpack_namespace(base_url, name)
        self.value = self.read()

    def read(self):
        try:
            var = get_url_json(self.url, timeout=3)[self.key]
            if self.type == 'json':
                return loads(var)
            elif self.type == 'plain':
                return var
            else:
                return None
        except:
            return None

    def write(self):
        try:
            if self.type == 'json':
                var = dumps(self.value)
            elif self.type == 'plain':
                var = self.value
            else:
                return False
            response = put_url(self.url, {self.key: var})
            return response['code'] == 'success'
        except:
            return False

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return self.write()

def global_wrapper(base_url, name):
    try:
        return GlobalVariable(base_url, name)
    except:
        return None
