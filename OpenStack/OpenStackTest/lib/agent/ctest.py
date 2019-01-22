# coding: utf-8
__author__ = 'Henry'
from flask import Flask, request
from flask_restful import Api, Resource, reqparse
from ConfigParser import ConfigParser
from lib.sqlite.connection import connection
from lib.utility import now, post_url, put_url, SimpleThread, global_wrapper, print_exception, register_api_resources, getip
from json import dumps, loads
from host_info import find_all_disk, get_default_disk, get_nfs_disk, get_sytem_info

agent_version = None
remote_base_url = None
server_port = None
server_entry = {}
instrusive_entry = {}
remote_key = '$REMOTE_BASE_URL'


TASK_STATUS = {
    'work': 0,
    'done': 1,
    'fail': -1
}


def load_remote_base_url_from_local():
    global remote_base_url
    global remote_key
    try:
        with connection.connect_db_row() as (db):
            res = db.query("SELECT value FROM local_table WHERE key='%s'" % remote_key)
            if res:
                remote_base_url = res[0]['value']
            else:
                if remote_base_url and len(remote_base_url) > 0:
                    db.execute_and_commit(['INSERT INTO local_table VALUES (?, ?)'], [
                     [
                      (
                       remote_key, remote_base_url)]])
    except:
        pass


def update_remote_base_url(db, new_url):
    global remote_base_url
    try:
        if new_url != remote_base_url:
            db.execute_and_commit(['UPDATE local_table SET value=? WHERE key=?'], [
             [
              (
               new_url, remote_key)]])
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
        with connection.connect_db_row() as (db):
            update_remote_base_url(db, new_url)
            tags = db.query('SELECT name, version FROM servtag_table')
            if tags:
                return {'tags': [ {'name': tag['name'], 'version': tag['version']} for tag in tags if tag ]}
            return {'tags': []}
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
        with connection.connect_db_row() as (db):
            subtasks = db.query('SELECT * FROM subtask_table')
            if subtasks:
                return {'subtasks': subtasks}
        return {'subtasks': '[]'}

    def post(self):
        global server_entry
        args = self.reqparse_post.parse_args()
        if args:
            subtask = {'id': args['id'], 'name': args['name'], 
               'args': args['args'], 
               'serv_id': args['serv_id'], 
               'task_id': args['task_id'], 
               'serv_name': args['serv_name'], 
               'serv_version': args['serv_version'], 
               'status': args['status']}
            with connection.connect_db() as (db):
                exist = db.query("SELECT * FROM subtask_table WHERE id='%s'" % args['id'])
                if not exist:
                    try:
                        entry_key = subtask['serv_name'] + subtask['serv_version']
                        print("accept request. . .\n")
                        print '++++++++++++++++++++++++++++++++++++++++++++++++++++++'
                        print("server name: ", subtask['serv_name'])
                        print '++++++++++++++++++++++++++++++++++++++++++++++++++++++'
                        print("start thread. . .\n")
                        if server_entry.has_key(entry_key):
                            entry = server_entry[entry_key]
                            db.execute_and_commit(['INSERT INTO subtask_table VALUES (?, ?, ?, ?, ?, ?, ?, ?)'], [
                             [
                              (
                               subtask['id'],
                               subtask['name'],
                               subtask['args'],
                               subtask['serv_id'],
                               subtask['task_id'],
                               subtask['serv_name'],
                               subtask['serv_version'],
                               subtask['status'])]])
                            print subtask['args']
                            SimpleThread(entry, subtask['id'], loads(subtask['args'].replace("'", '"').replace('u', '')) if subtask['args'] else '').start()
                            return {'code': 'success', 'id': subtask['id']}
                    except Exception as e:
                        print e

        return {'code': 'error'}

    def delete(self):
        with connection.connect_db() as (db):
            db.execute_and_commit(['DELETE FROM subtask_table'])
            return {'code': 'success'}
        return {'code': 'error'}


class SubTaskAgentID(Resource):

    def get(self, subtask_id):
        with connection.connect_db_row() as (db):
            subtasks = db.query("SELECT * FROM subtask_table WHERE id='%s'" % subtask_id)
            if subtasks:
                return {'subtask': subtasks[0]}
        return {'subtask': '[]'}

    def delete(self):
        args = self.reqparse_post.parse_args()
        if args:
            with connection.connect_db() as (db):
                subtask_id = args['id']
                db.execute_and_commit(['DELETE FROM subtask_table WHERE id=?'], [[(subtask_id,)]])
                return {'code': 'success', 'id': subtask_id}
        return {'code': 'error'}


def register_service(service_name, version):
    try:
        with connection.connect_db() as (db):
            # print '%s %s '% (service_name, version)
            res = db.query("SELECT name FROM servtag_table WHERE name='%s' AND version='%s'" % (
             service_name, version))
            if not res:
                db.execute_and_commit(['INSERT INTO servtag_table VALUES (?, ?)'], [
                 [
                  (
                   service_name, version)]])
    except Exception as e:
        print_exception(__name__, e)


def unregister_service(service_name, version):
    try:
        with connection.connect_db() as (db):
            db.execute_and_commit(['DELETE FROM servtag_table WHERE name=? AND version=?'], [
             [
              (
               service_name, version)]])
    except Exception as e:
        print_exception(__name__, e)


class TaskRequest:

    @staticmethod
    def set_subtask_status(subtask_id, status):
        with connection.connect_db() as (db):
            db.execute_and_commit(['UPDATE subtask_table SET status=? WHERE id=?'], [
             [
              (
               status, subtask_id)]])
            return True
        return False

    @staticmethod
    def put_subtask_status(subtask_id, status):
        with connection.connect_db_row() as (db):
            result = db.query("SELECT name, args FROM subtask_table WHERE id='%s'" % subtask_id)
            if result:
                name = result[0]['name']
                args = result[0]['args']
                url = '%s/switch/subtask/%s' % (remote_base_url, subtask_id)
                payload = {'name': name, 
                   'args': args, 
                   'report_id': '', 
                   'status': status}
                put_url(url, payload)

    @staticmethod
    def post_report(subtask_id, severity, result, brief, detail, json_data=None):
        payload = {
            'severity': severity,
            'result': result,
            'brief': brief,
            'detail': detail,
            'subtask_id': subtask_id,
            'timestamp': now()}
        if json_data:
            payload['json_data'] = dumps(json_data)
#         post_url('%s/switch/report' % remote_base_url, payload)
            post_url('%s/openStack/reportReturn' % remote_base_url, payload)
            

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
        global instrusive_entry
        try:
#             post_args = self.reqparse_post.parse_args()
            post_args = {}
            post_args['name'] = 'openvas_available'
            post_args['args'] = 0
            name = post_args['name']
            args = post_args['args']
            if name:
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
    def __init__(self, module_name):
        global agent_version
        global remote_base_url
        global server_port
        self.module_name = module_name
        self.modules = None
        self.local_key = None
        self.agent_port = None
        self.debug_mode = True
        self.multi_thread = False
        self.services_online = []
        try:
            config_name = '%s.conf' % __name__
            self.config = ConfigParser()
            self.config.read(config_name)
            server_port = int(self.config.get('network', 'server-port', '5000'))
            db_filename = self.config.get('database', 'file', ':memory:')
            agent_version = self.config.get('system', 'version', '1.0.3')
            #remote base url
            remote_base_url = self.config.get('network', 'server-base', 'http://localhost:5000')
            self.local_key = self.config.get('module', 'local-key', 'agent_path')
            paths = self.config.get('module', 'path', '')
            if paths:
                self.modules = str(paths).split(';')
                # connection database
            connection(db_filename).prepare()
            self.app = Flask(self.module_name)
            # register_api_resources(Api(self.app), API_MAP, '/switch/agent/')
            register_api_resources(Api(self.app), API_MAP, '')
        except Exception as e:
            print 'Error on initialization.\nPlease check if the config file name is "%s"' % config_name
            print_exception(__name__, e)

        return

    def post_ip(self):
        payload = {
            'ip': getip(),
            'port': self.agent_port,
            'type': 0}
        post_url('%s/switch/ip' % remote_base_url, payload)

    # 注册节点信息
    def post_host_info(self):
        from host_info import get_sytem_info
        print '%s/nodeRegister' % remote_base_url
        post_url('%s/nodeRegister' % remote_base_url, payload=get_sytem_info())

    def entry(self, service_name, version='1.0.1'):
        def register_entry(F):
            try:
                # print service_name, version,'a'
                service = service_name + version
                register_service(service_name, version)
                server_entry[service] = F
                self.services_online.append({'name': service_name, 'version': version})
            except:
                pass
            return F

        return register_entry

    @staticmethod
    def instrusive(F):
        try:
            function_name = F.__name__
            instrusive_entry[function_name] = F
        except:
            pass
        return F

    def tell_online_services(self):
        for service in self.services_online:
            TaskRequest.post_servtag(service['name'], service['version'], self.agent_port)

    @staticmethod
    def post_report(subtask_id, severity, result, brief, detail, json_data=None):
        # global TASK_STATUS
        # TaskRequest.set_subtask_status(subtask_id, TASK_STATUS['done'])
        # TaskRequest.put_subtask_status(subtask_id, TASK_STATUS['done'])
        TaskRequest.post_report(subtask_id, severity, result, brief, detail, json_data)

    @staticmethod
    def post_failure(subtask_id):
        TaskRequest.set_subtask_status(subtask_id, TASK_STATUS['fail'])
        TaskRequest.put_subtask_status(subtask_id, TASK_STATUS['fail'])

    @staticmethod
    def get_global(global_key):
        var = global_wrapper(remote_base_url, global_key)
        if var:
            return var.value
        return

    @staticmethod
    def set_global(global_key, global_value):
        var = global_wrapper(remote_base_url, global_key)
        if var:
            var.value = global_value
            return var.write()
        return

    @staticmethod
    def global_wrapper(global_key):
        return global_wrapper(remote_base_url, global_key)

    @staticmethod
    def get_local(local_key):
        with connection.connect_db_row() as (db):
            result = db.query("SELECT value FROM local_table WHERE key='%s'" % local_key)
            if result:
                return result[0]['value']
            return
        return

    @staticmethod
    def set_local(local_key, local_value):
        with connection.connect_db() as (db):
            result = db.query("SELECT key FROM local_table WHERE key='%s'" % local_key)
            if result:
                db.execute_and_commit(['UPDATE local_table SET value=? WHERE key=?'], [
                 [
                  (
                   local_value, local_key)]])
            else:
                db.execute_and_commit(['INSERT INTO local_table VALUES(?, ?)'], [
                 [
                  (
                   local_key, local_value)]])
            return True
        return False

    def run(self):
        try:
            self.agent_port = int(self.config.get('network', 'agent-port', '9099'))
            self.debug_mode = self.config.getboolean('system', 'debug')
            self.multi_thread = self.config.getboolean('system', 'multi-thread')
            # 不用注册远程方法了
            # self.tell_online_services()

            # 暂时不用
            # self.post_ip()
            # self.post_host_info()
            result = post_url('%s/openStack/initRegister' % remote_base_url, payload=get_nfs_disk())
            post_url('%s/openStack/nodeRegister' % remote_base_url, payload=get_sytem_info())
            print('register result: ', result)
            self.app.run(host='0.0.0.0',
                         port=self.agent_port,
                         debug=self.debug_mode,
                         use_reloader=self.debug_mode,
                         threaded=self.multi_thread)
        except Exception as e:
            print_exception(__name__, e)