# -*- coding: utf-8 -*-
__author__ = 'Henry'

from flask import Flask, request
from flask_restful import Api, Resource, reqparse
from ConfigParser import ConfigParser
from lib.sqlite.connection import connection
from lib.utility import now, post_url, put_url, SimpleThread, \
    global_wrapper, print_exception, register_api_resources,getip
from requests import get
from json import dumps, loads
from info.virt_info import get_vm_disks_for_enc
from lib.utility import getip
from .host_info import get_sytem_info

# Agent version
agent_version = None
# Switch server base url
remote_base_url = None
# Switch server port
server_port = None
# Service entries
server_entry = {}
# Instrusive entries
instrusive_entry = {}
# Local Remote URL Key
remote_key = '$REMOTE_BASE_URL'
# Task&SubTask status value
TASK_STATUS = {
    'work': 0,
    'done': 1,
    'fail': -1
}

def load_remote_base_url_from_local():
    try:
        with connection.connect_db_row() as db:
            global remote_key
            global remote_base_url

            res = db.query("SELECT value FROM local_table WHERE key='%s'" % remote_key)
            if res:
                remote_base_url = res[0]['value']
            elif remote_base_url and len(remote_base_url) > 0:
                db.execute_and_commit(["INSERT INTO local_table VALUES (?, ?)"],
                                      [[(remote_key, remote_base_url,)]])
    except:
        pass

def update_remote_base_url(db, new_url):
    try:
        global remote_base_url

        if new_url != remote_base_url:
            db.execute_and_commit(["UPDATE local_table SET value=? WHERE key=?"],
                                  [[(new_url, remote_key,)]])
            remote_base_url = new_url
    except:
        pass


class VersionInfo(Resource):
    def get(self):
        global agent_version
        return {'version': agent_version}


class HeartRequest(Resource):
    def get(self):
        return {"status": "true"}

class ServtagRequest(Resource):
    def get(self):
        global server_port

        new_url = 'http://%s:%d' % (request.remote_addr, server_port)

        with connection.connect_db_row() as db:
            update_remote_base_url(db, new_url)
            tags = db.query("SELECT name, version FROM servtag_table")
            return {'tags': [{'name': tag['name'], 'version': tag['version']}
                             for tag in tags if tag]} if tags else {'tags': []}
        return {'code': 'error'}

class SubTaskAgent(Resource):
    def __init__(self):
        self.reqparse_post = reqparse.RequestParser()
        self.reqparse_post.add_argument('id', type=str, location='json', required=True, help='need subtask_id')
        self.reqparse_post.add_argument('name', type=str, location='json', required=True, help='need name')
        self.reqparse_post.add_argument('args', type=str, location='json')
        self.reqparse_post.add_argument('serv_id', type=str, location='json', required=True, help='need serv_id')
        self.reqparse_post.add_argument('task_id', type=str, location='json', required=True, help='need task_id')
        self.reqparse_post.add_argument('serv_name', type=str, location='json', required=True, help='need serv_name')
        self.reqparse_post.add_argument('serv_version', type=str, location='json', required=True, help='need serv_version')
        self.reqparse_post.add_argument('status', type=int, location='json', required=True, help='need status')
        self.reqparse_delete = reqparse.RequestParser()
        self.reqparse_delete.add_argument('id', type=str, location='json', required=True, help='need subtask_id')
        super(SubTaskAgent, self).__init__()

    def get(self):
        with connection.connect_db_row() as db:
            subtasks = db.query("SELECT * FROM subtask_table")
            if subtasks:
                return {'subtasks': subtasks}
        return {'subtasks': '[]'}

    def post(self):
        args = self.reqparse_post.parse_args()
        if args:
            subtask = {
                'id': args['id'],
                'name': args['name'],
                'args': args['args'],
                'serv_id': args['serv_id'],
                'task_id': args['task_id'],
                'serv_name': args['serv_name'],
                'serv_version': args['serv_version'],
                'status': args['status']
                }
            with connection.connect_db() as db:
                exist = db.query("SELECT * FROM subtask_table WHERE id='%s'" % args['id'])
                if not exist:
                    try:
                        global server_entry
                        print("accept request. . .\n")
                        print '++++++++++++++++++++++++++++++++++++++++++++++++++++++'
                        print("server name: ", subtask['serv_name'])
                        print '++++++++++++++++++++++++++++++++++++++++++++++++++++++'
                        print("start thread. . .\n")
                        entry_key = subtask['serv_name'] + subtask['serv_version']
                        if server_entry.has_key(entry_key):
                            entry = server_entry[entry_key]
                            db.execute_and_commit(["INSERT INTO subtask_table VALUES (?, ?, ?, ?, ?, ?, ?, ?)"],
                                              [[(subtask['id'],
                                                 subtask['name'],
                                                 subtask['args'],
                                                 subtask['serv_id'],
                                                 subtask['task_id'],
                                                 subtask['serv_name'],
                                                 subtask['serv_version'],
                                                 subtask['status'], )]])
                            SimpleThread(entry, subtask['id'], loads(subtask['args'].replace("'", '"').replace('u', ''))
                                if subtask['args'] else '').start()
                            return {'code': 'success', 'id': subtask['id']}
                    except:
                        pass
        return {'code': 'error'}

    def delete(self):
        with connection.connect_db() as db:
            db.execute_and_commit(["DELETE FROM subtask_table"])
            return {'code': 'success'}
        return {'code': 'error'}


class SubTaskAgentID(Resource):
    def get(self, subtask_id):
        with connection.connect_db_row() as db:
            subtasks = db.query("SELECT * FROM subtask_table WHERE id='%s'" % subtask_id)
            if subtasks:
                return {'subtask': subtasks[0]}
        return {'subtask': '[]'}

    def delete(self):
        args = self.reqparse_post.parse_args()
        if args:
            with connection.connect_db() as db:
                subtask_id = args['id']
                db.execute_and_commit(["DELETE FROM subtask_table WHERE id=?"], [[(subtask_id,)]])
                return {'code': 'success', 'id': subtask_id}
        return {'code': 'error'}


def register_service(service_name, version):
    try:
        with connection.connect_db () as db:
            res = db.query("SELECT name FROM servtag_table WHERE name='%s' "
                           "AND version='%s'" % (service_name, version))
            if not res:
                db.execute_and_commit(["INSERT INTO servtag_table VALUES (?, ?)"],
                                      [[(service_name, version,)]])
    except Exception, e:
        print_exception(__name__, e)


def unregister_service(service_name, version):
    try:
        with connection.connect_db () as db:
            db.execute_and_commit(["DELETE FROM servtag_table WHERE name=? AND version=?"],
                                  [[(service_name, version, )]])
    except Exception, e:
        print_exception(__name__, e)


class TaskRequest:
    @staticmethod
    def set_subtask_status(subtask_id, status):
        with connection.connect_db() as db:
            db.execute_and_commit(["UPDATE subtask_table SET status=? WHERE id=?"],
                                  [[(status, subtask_id,)]])
            return True
        return False

    @staticmethod
    def put_subtask_status(subtask_id, status):
        with connection.connect_db_row() as db:
            result = db.query("SELECT name, args FROM subtask_table WHERE id='%s'" % subtask_id)
            if result:
                name = result[0]['name']
                args = result[0]['args']
                url = '%s/switch/subtask/%s' % (remote_base_url, subtask_id)
                payload = {
                    'name': name,
                    'args': args,
                    'report_id': '',
                    'status': status
                }
                put_url(url, payload)

    @staticmethod
    def post_report(subtask_id, severity, result, brief, detail, json_data=None):
        payload = {
            'severity': severity,
            'result': result,
            'brief': brief,
            'detail': detail,
            'subtask_id': subtask_id,
            'timestamp': now()
        }
        if json_data:
            payload['json_data'] = dumps(json_data)
        post_url('%s/oVirt/reportReturn' % remote_base_url, payload)

    @staticmethod
    def post_servtag(serv_name, version, port):
        try:
            url = '%s/switch/servtag/%s' % (remote_base_url, serv_name)
            post_url(url, payload={'name': serv_name, 'version': version, 'port': port}, timeout=2)
        except:
            pass


class InstrusiveInvoker(Resource):
    def __init__(self):
        self.reqparse_post = reqparse.RequestParser()
        self.reqparse_post.add_argument('name', type=str, location='json', required=True, help='need name')
        self.reqparse_post.add_argument('args', type=str, location='json')
        super(InstrusiveInvoker, self).__init__()

    def post(self):
        try:
            post_args = self.reqparse_post.parse_args()
            name = post_args['name']
            args = post_args['args']
            if name:
                global instrusive_entry

                function = instrusive_entry[name]
                if function:
                    result = function(loads(args) if args else None)
                    return {'result': result}
        except:
            pass
        return {'code': 'error'}    

API_MAP = {
    'version': VersionInfo,
    'servtag': ServtagRequest,
    'switch/agent/subtask': SubTaskAgent,
    'subtask/<string:subtask_id>': SubTaskAgentID,
    'instrusive': InstrusiveInvoker,
    'nodeIsExist': HeartRequest
}


class SwitchAgent:
    #读取配置文件，注册agent  restful api
    def __init__(self, module_name):
        self.module_name = module_name
        self.modules = None
        self.local_key = None
        # Agent port
        self.agent_port = None
        # Debug mode switch
        self.debug_mode = True
        # Multi-thread mode switch
        self.multi_thread = False
        # Servtag online table
        self.services_online = []

        global server_port
        global agent_version
        global remote_base_url

        # Load configuration
        try:
            config_name = '%s.conf' % __name__
            self.config = ConfigParser()
            self.config.read(config_name)
            self.agent_port = int(self.config.get('network', 'agent-port', '9099'))
            
            server_port = int(self.config.get('network', 'server-port', '8083'))
            db_filename = self.config.get('database', 'file', ':memory:')
            agent_version = self.config.get('system', 'version', '1.0.3')
            remote_base_url = self.config.get('network', 'server-base', 'http://localhost:8083')
            self.local_key = self.config.get('module', 'local-key', 'agent_path')
            paths = self.config.get('module', 'path', '')
            if paths:
                self.modules = str(paths).split(';')

            # Prepare database
            connection(db_filename).prepare()

            # Load Server Base URL
            # load_remote_base_url_from_local()

            # Initialize service
            self.app = Flask(self.module_name)
            # register_api_resources(Api(self.app), API_MAP, '/switch/agent')
            register_api_resources(Api(self.app), API_MAP, '')

        except Exception, e:
            print 'Error on initialization.\nPlease check if the config file name is "%s"' % config_name
            print_exception(__name__, e)
        #向数据库写入此agent所代理的服务名称和版本号
    def entry(self, service_name, version='1.0.1'):
        def register_entry(F):
            try:
                global server_entry
                service = service_name + version
                # print service
                register_service(service_name, version)
                server_entry[service] = F
                #将服务和版本信息保存到service_online中，向switch注册时需用到
                self.services_online.append({'name': service_name, 'version': version})
            except:
                pass
            return F
        return register_entry

    def post_ip(self):
        payload = {
            'ip': getip(),
            'port': self.agent_port,
            'type': 1
        }
        post_url('%s/switch/ip' % remote_base_url, payload)

    # 注册节点信息
    def post_host_info(self):
        from host_info import get_sytem_info
        post_url('%s/nodeRegister' % remote_base_url, payload=get_sytem_info())

    @staticmethod
    def instrusive(F):
        try:
            global instrusive_entry
            function_name = F.__name__
            instrusive_entry[function_name] = F
        except:
            pass
        return F

    # Only be called after get agent-port config value
    def tell_online_services(self):
        for service in self.services_online:
            #向switch注册服务名称及版本号
            TaskRequest.post_servtag(service['name'], service['version'], self.agent_port)

    @staticmethod
    def post_report(subtask_id, severity, result, brief, detail, json_data=None):
        # global TASK_STATUS
        # TaskRequest.set_subtask_status(subtask_id, TASK_STATUS['done'])
        # TaskRequest.put_subtask_status(subtask_id, TASK_STATUS['done'])
        TaskRequest.post_report(subtask_id, severity, result, brief, detail, json_data)

    @staticmethod
    def post_failure(subtask_id):
        global TASK_STATUS
        TaskRequest.set_subtask_status(subtask_id, TASK_STATUS['fail'])
        TaskRequest.put_subtask_status(subtask_id, TASK_STATUS['fail'])

    @staticmethod
    def get_global(global_key):
        var = global_wrapper(remote_base_url, global_key)
        return var.value if var else None

    @staticmethod
    def set_global(global_key, global_value):
        var = global_wrapper(remote_base_url, global_key)
        if var:
            var.value = global_value
            return var.write()
        else: return None

    @staticmethod
    def global_wrapper(global_key):
        return global_wrapper(remote_base_url, global_key)

    @staticmethod
    def get_local(local_key):
        with connection.connect_db_row() as db:
            result = db.query("SELECT value FROM local_table WHERE key='%s'" % local_key)
            return result[0]['value'] if result else None
        return None

    @staticmethod
    def set_local(local_key, local_value):
        with connection.connect_db() as db:
            result = db.query("SELECT key FROM local_table WHERE key='%s'" % local_key)
            if result:
                db.execute_and_commit(["UPDATE local_table SET value=? WHERE key=?"],
                                      [[(local_value, local_key,)]])
            else:
                db.execute_and_commit(["INSERT INTO local_table VALUES(?, ?)"],
                                      [[(local_key, local_value,)]])
            return True
        return False

    def run(self):
        try:
            #读取配置文件
            self.agent_port = int(self.config.get('network', 'agent-port', '9099'))
            self.debug_mode = self.config.getboolean('system', 'debug')
            self.multi_thread = self.config.getboolean('system', 'multi-thread')

            # Tell switch server about what service is online
            # self.tell_online_services()
            # self.post_ip()
            # 获取磁盘信息保存到全局变量中
            self.post_host_info()
            # vmpath=self.global_wrapper('json@storage:disk')
            vmpath = {'disk': [get_vm_disks_for_enc(), getip(), self.agent_port]}
            post_url('%s/oVirt/initRegister' % remote_base_url, payload=vmpath)
            post_url('%s/oVirt/nodeRegister' % remote_base_url, payload=get_sytem_info())
            print 'value: ', vmpath
            print 'system: ', get_sytem_info()
            # vmpath.write()
            # Run services
            self.app.run(host='0.0.0.0',
                         port=self.agent_port,
                         debug=self.debug_mode,
                         use_reloader=self.debug_mode,
                         threaded=self.multi_thread)
        except Exception, e:
            print_exception(__name__, e)

