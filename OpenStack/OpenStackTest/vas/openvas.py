__author__ = 'Henry'

from os import popen
from xml.dom.minidom import parseString

def omp_wrapper(global_wrap):
    try:
        omp_info = global_wrap('json@openvas:omp')
        if not omp_info.value:
            return None

        username = omp_info.value['username']
        password = omp_info.value['password']
        if omp_info.value.has_key('port'):
            port = omp_info.value['port']
        else:
            port = None
        if omp_info.value.has_key('host'):
            host = omp_info.value['host']
        else:
            host = None

        omp = OMP(username=username, password=password, port=port, host=host)
        if omp is not None:
            return omp
    except BaseException, e:
        print e.message
    return None


class OMP:
    def __init__(self, username, password, port=None, host=None):
        self.base_command = 'omp -u %s -w %s ' % (username, password)
        if port:
            self.base_command += '-p %s ' % port
        if host:
            self.base_command += '-h %s ' % host

    @staticmethod
    def raw_pipe(command):
        pipe = popen(command)
        data = pipe.read()
        pipe.close()
        return data

    def read_pipe(self, command):
        return OMP.raw_pipe(self.base_command + command)

    @staticmethod
    def ping():
        resp = OMP.raw_pipe('omp --ping')
        return resp.find('success') != -1

    @staticmethod
    def __node_value(node):
        return str(node.childNodes[0].nodeValue) if node and node.childNodes else ''

    @staticmethod
    def __select_name_node(nodes):
        if nodes:
            name_node = None
            name_count = len(nodes)
            if name_count > 1:
                name_node = nodes[1]
            elif name_count == 1:
                name_node = nodes[0]
            return name_node
        return None

    @staticmethod
    def __child(parent, child_name, index=0):
        if parent is None or not child_name:
            return None
        childs = parent.getElementsByTagName(child_name)
        if childs:
            try:
                return childs[index]
            except:
                pass
        return None

    @staticmethod
    def __child_value(parent, child_name, index=0):
        child = OMP.__child(parent=parent, child_name=child_name, index=index)
        return OMP.__node_value(child) if child else ''

    @staticmethod
    def __to_int(raw_str):
        try:
            return int(raw_str)
        except:
            return 0

    @staticmethod
    def __to_float(raw_str):
        try:
            return float(raw_str)
        except:
            return 0.0

    def create_target(self, name, ip_list):
        try:
            hosts = ''
            for ip in ip_list:
                hosts += '%s,' % ip
            if ip_list:
                hosts = hosts[:-1]
            target_command = "-X '<create_target><name>%s</name>" \
                             "<hosts>%s</hosts></create_target>'" % (name, hosts)
            response = self.read_pipe(target_command)
            if response:
                doc = parseString(response)
                root = doc.documentElement
                status = root.getAttribute('status')
                if status[:2] == '20':
                    return root.getAttribute('id')
        except BaseException, e:
            print e.message
        return None

    def delete_target(self, target_id):
        try:
            target_command = "-X '<delete_target target_id=\"%s\"/>'" % target_id
            response = self.read_pipe(target_command)
            if response:
                doc = parseString(response)
                root = doc.documentElement
                status = root.getAttribute('status')
                return status[:2] == '20'
        except BaseException, e:
            print e.message
        return None

    def create_task(self, name, target_id, config_id, comment=None):
        try:
            if comment is None:
                comment = ''
            task_command = "-X '<create_task><name>%s</name><comment>%s</comment>" \
                           "<config id=\"%s\"/><target id=\"%s\"/></create_task>'" % \
                           (name, comment, config_id, target_id)
            response = self.read_pipe(task_command)
            if response:
                doc = parseString(response)
                root = doc.documentElement
                status = root.getAttribute('status')
                if status[:2] == '20':
                    return root.getAttribute('id')
        except BaseException, e:
            print e.message
        return None

    def delete_task(self, task_id):
        try:
            task_command = "-X '<delete_task task_id=\"%s\"/>'" % task_id
            response = self.read_pipe(task_command)
            if response:
                doc = parseString(response)
                root = doc.documentElement
                status = root.getAttribute('status')
                return status[:2] == '20'
        except BaseException, e:
            print e.message
        return None

    def start_task(self, task_id):
        try:
            task_command = "-X '<start_task task_id=\"%s\"/>'" % task_id
            response = self.read_pipe(task_command)
            if response:
                doc = parseString(response)
                root = doc.documentElement
                status = root.getAttribute('status')
                return status[:2] == '20'
        except BaseException, e:
            print e.message
        return False

    def stop_task(self, task_id):
        try:
            task_command = "-X '<stop_task task_id=\"%s\"/>'" % task_id
            response = self.read_pipe(task_command)
            if response:
                doc = parseString(response)
                root = doc.documentElement
                status = root.getAttribute('status')
                return status[:2] == '20'
        except BaseException, e:
            print e.message
        return False

    def pause_task(self, task_id):
        try:
            task_command = "-X '<pause_task task_id=\"%s\"/>'" % task_id
            response = self.read_pipe(task_command)
            if response:
                doc = parseString(response)
                root = doc.documentElement
                status = root.getAttribute('status')
                return status[:2] == '20'
        except BaseException, e:
            print e.message
        return False

    def resume_task(self, task_id):
        try:
            task_command = "-X '<resume_paused_task task_id=\"%s\"/>'" % task_id
            response = self.read_pipe(task_command)
            if response:
                doc = parseString(response)
                root = doc.documentElement
                status = root.getAttribute('status')
                return status[:2] == '20'
        except BaseException, e:
            print e.message
        return False

    def get_version(self):
        try:
            config_command = "-X '<get_version/>'"
            response = self.read_pipe(config_command)
            if response:
                doc = parseString(response)
                root = doc.documentElement
                status = root.getAttribute('status')
                if status[:2] == '20':
                    return OMP.__child_value(root, 'version')
        except BaseException, e:
            print e.message
        return None

    def __proc_target(self, node):
        target_id = node.getAttribute('id')
        target_name = ''
        target_hosts = []
        name_nodes = node.getElementsByTagName('name')
        if name_nodes:
            name_node = OMP.__select_name_node(name_nodes)
            if name_node:
                target_name = OMP.__node_value(name_node)
        host_node = OMP.__child(node, 'hosts')
        if host_node:
            target_hosts = filter(lambda x: not not x,
                                  OMP.__node_value(host_node).split(','))
        data = {
            'id': target_id,
            'name': target_name,
            'hosts': target_hosts
        }
        return data

    def get_targets(self, target_id=None):
        try:
            if target_id:
                target_command = "-X '<get_targets target_id=\"%s\" task=\"1\"/>'" % target_id
            else:
                target_command = "-X '<get_targets/>'"
            response = self.read_pipe(target_command)
            if response:
                doc = parseString(response)
                root = doc.documentElement
                status = root.getAttribute('status')
                if status[:2] == '20':
                    target_nodes = root.getElementsByTagName('target')
                    if target_nodes:
                        targets = []
                        for target_node in target_nodes:
                            try:
                                data = self.__proc_target(target_node)
                                if data:
                                    targets.append(data)
                            except:
                                pass
                        return targets, root
        except BaseException, e:
            print e.message
        return None

    def __proc_task(self, node):
        task_id = node.getAttribute('id')
        task_name = ''
        task_target_id = ''
        task_target_name = ''
        task_config_id = ''
        task_config_name = ''
        task_scanner_id = ''
        task_scanner_name = ''
        task_last_report = ''

        name_nodes = node.getElementsByTagName('name')
        if name_nodes:
            name_node = OMP.__select_name_node(name_nodes)
            if name_node:
                task_name = OMP.__node_value(name_node)
        task_comment = OMP.__child_value(node, 'comment')
        task_status = OMP.__child_value(node, 'status')

        raw_report_count = OMP.__child_value(node, 'report_count')
        task_report_count = OMP.__to_int(raw_report_count)

        if task_report_count > 0:
            try:
                last_report_node = node.getElementsByTagName('last_report')[0]
                report_node = last_report_node.getElementsByTagName('report')[0]
                task_last_report = report_node.getAttribute('id')
            except:
                pass

        config_node = OMP.__child(node, 'config')
        if config_node:
            task_config_id = config_node.getAttribute('id')
            task_config_name = OMP.__child_value(config_node, 'name')
        target_node = OMP.__child(node, 'target')
        if target_node:
            task_target_id = target_node.getAttribute('id')
            task_target_name = OMP.__child_value(target_node, 'name')
        scanner_node = OMP.__child(node, 'scanner')
        if scanner_node:
            task_scanner_id = scanner_node.getAttribute('id')
            task_scanner_name = OMP.__child_value(scanner_node, 'name')

        data = {
            'id': task_id,
            'name': task_name,
            'comment': task_comment,
            'status': task_status,
            'last_report_id': task_last_report,
            'report_count': task_report_count,
            'target_id': task_target_id,
            'target_name': task_target_name,
            'config_id': task_config_id,
            'config_name': task_config_name,
            'scanner_id': task_scanner_id,
            'scanner_name': task_scanner_name
        }
        return data

    def get_tasks(self, task_id=None):
        try:
            if task_id:
                task_command = "-X '<get_tasks task_id=\"%s\" details=\"1\"/>'" % task_id
            else:
                task_command = "-X '<get_tasks/>'"
            response = self.read_pipe(task_command)
            if response:
                doc = parseString(response)
                root = doc.documentElement
                status = root.getAttribute('status')
                if status[:2] == '20':
                    task_nodes = root.getElementsByTagName('task')
                    if task_nodes:
                        tasks = []
                        for task_node in task_nodes:
                            try:
                                data = self.__proc_task(task_node)
                                if data:
                                    tasks.append(data)
                            except:
                                pass
                        return tasks, root
        except BaseException, e:
            print e.message
        return None

    def __proc_report(self, node):
        report_id = node.getAttribute('id')
        report_name = ''
        report_task_id = ''
        report_task_name = ''
        report_format_id = ''
        report_format_name = ''

        name_nodes = node.getElementsByTagName('name')
        if name_nodes:
            name_node = OMP.__select_name_node(name_nodes)
            if name_node:
                report_name = OMP.__node_value(name_node)

        report_comment = OMP.__child_value(node, 'comment')

        task_node = OMP.__child(node, 'task')
        if task_node:
            report_task_id = task_node.getAttribute('id')
            report_task_name = OMP.__child_value(task_node, 'name')

        format_node = OMP.__child(node, 'report_format')
        if format_node:
            report_format_id = format_node.getAttribute('id')
            report_format_name = OMP.__child_value(format_node, 'name')

        nodes = node.getElementsByTagName('report')
        if not nodes:
            data = {
                'id': report_id,
                'name': report_name,
                'comment': report_comment,
                'task_id': report_task_id,
                'task_name': report_task_name,
                'format_id': report_format_id,
                'format_name': report_format_name
            }
            return data
        node = nodes[0]

        report_run_status = OMP.__child_value(node, 'scan_run_status')

        report_host_count = 0
        hosts_node = OMP.__child(node, 'hosts')
        if hosts_node:
            raw_host_count = OMP.__child_value(hosts_node, 'count')
            report_host_count = OMP.__to_int(raw_host_count)

        report_vulns_count = 0
        vulns_node = OMP.__child(node, 'vulns')
        if vulns_node:
            raw_vulns_count = OMP.__child_value(vulns_node, 'count')
            report_vulns_count = OMP.__to_int(raw_vulns_count)

        report_target_id = ''
        task_node = OMP.__child(node, 'task')
        if task_node:
            target_node = OMP.__child(task_node, 'target')
            if target_node:
                report_target_id = target_node.getAttribute('id')

        report_port_info = {'count': 0, 'detail': []}
        port_node = OMP.__child(node, 'ports')
        if port_node:
            port_nodes = port_node.getElementsByTagName('port')
            raw_port_count = OMP.__child_value(port_node, 'count')
            report_port_info['count'] = OMP.__to_int(raw_port_count)
            port_list = []
            if port_nodes:
                for n in port_nodes:
                    try:
                        port_data = OMP.__node_value(n)
                        host_data = OMP.__child_value(n, 'host')
                        severity_data = OMP.__child_value(n, 'severity')
                        threat_data = OMP.__child_value(n, 'threat')
                        port = {
                            'port': port_data,
                            'host': host_data,
                            'severity': severity_data,
                            'threat': threat_data
                        }
                        port_list.append(port)
                    except:
                        pass
            report_port_info['detail'] = port_list

        report_results = []
        results_node = OMP.__child(node, 'results')
        if results_node:
            result_nodes = results_node.getElementsByTagName('result')
            if result_nodes:
                for result_node in result_nodes:
                    try:
                        result_id = result_node.getAttribute('id')
                        result_name = OMP.__child_value(result_node, 'name')
                        result_host = OMP.__child_value(result_node, 'host')
                        result_port = OMP.__child_value(result_node, 'port')
                        result_nvt_version = OMP.__child_value(result_node, 'scan_nvt_version')
                        result_threat = OMP.__child_value(result_node, 'threat')
                        result_severity = OMP.__to_float(OMP.__child_value(result_node, 'severity'))
                        result_description = OMP.__child_value(result_node, 'description')
                        nvt_node = OMP.__child(result_node, 'nvt')
                        if nvt_node:
                            nvt_oid = nvt_node.getAttribute('oid')
                            nvt_name = OMP.__child_value(nvt_node, 'name')
                            nvt_family = OMP.__child_value(nvt_node, 'family')
                            nvt_cvss_base = OMP.__child_value(nvt_node, 'cvss_base')
                            nvt_cve = OMP.__child_value(nvt_node, 'cve')
                            nvt_bid = OMP.__child_value(nvt_node, 'bid')
                            nvt_xref = OMP.__child_value(nvt_node, 'xref')
                            nvt_tags = OMP.__child_value(nvt_node, 'tags')
                        result_qod = 0
                        qod_node = OMP.__child(result_node, 'qod')
                        if qod_node:
                            result_qod = OMP.__to_int(OMP.__child_value(qod_node, 'value'))
                        result_unit = {
                            'id': result_id,
                            'name': result_name,
                            'host': result_host,
                            'port': result_port,
                            'threat': result_threat,
                            'severity': result_severity,
                            'qod': result_qod,
                            'description': result_description,
                            'nvt_version': result_nvt_version,
                            'nvt_oid': nvt_oid,
                            'nvt_name': nvt_name,
                            'nvt_family': nvt_family,
                            'nvt_cvss_base': nvt_cvss_base,
                            'nvt_cve': nvt_cve,
                            'nvt_bid': nvt_bid,
                            'nvt_xref': nvt_xref,
                            'nvt_tags': nvt_tags
                        }
                        report_results.append(result_unit)
                    except:
                        pass

        data = {
            'id': report_id,
            'name': report_name,
            'comment': report_comment,
            'status': report_run_status,
            'task_id': report_task_id,
            'task_name': report_task_name,
            'target_id': report_target_id,
            'format_id': report_format_id,
            'format_name': report_format_name,
            'host_count': report_host_count,
            'vulns_count': report_vulns_count,
            'ports': report_port_info,
            'results': report_results
        }
        return data

    def get_reports(self, report_id=None, task_id=None):
        try:
            if report_id:
                target_command = "-X '<get_reports report_id=\"%s\"/>'" % report_id
            else:
                target_command = "-X '<get_reports/>'"
            response = self.read_pipe(target_command)
            if response:
                doc = parseString(response)
                root = doc.documentElement
                status = root.getAttribute('status')
                if status[:2] == '20':
                    report_nodes = [childNode for childNode in root.childNodes
                                    if childNode and childNode.nodeName == 'report']
                    if report_nodes:
                        reports = []
                        for report_node in report_nodes:
                            try:
                                data = self.__proc_report(report_node)
                                if data:
                                    reports.append(data)
                            except:
                                pass
                        return reports, root
        except BaseException, e:
            print e.message
        return None

    def get_results(self, result_id=None, task_id=None):
        try:
            if result_id:
                if task_id:
                    target_command = "-X '<get_results result_id=\"%s\" task_id=\"%s\"/>'" % (result_id, task_id)
                else:
                    target_command = "-X '<get_results result_id=\"%s\"/>'" % result_id
            else:
                target_command = "-X '<get_results/>'"
            response = self.read_pipe(target_command)
            if response:
                doc = parseString(response)
                root = doc.documentElement
                status = root.getAttribute('status')
                return root if status[:2] == '20' else None
        except BaseException, e:
            print e.message
        return None

    def get_nvts(self, nvt_oid=None):
        try:
            if nvt_oid:
                target_command = "-X '<get_nvts details=\"1\" timeout=\"1\" " \
                                 "preference_count=\"1\" preferences=\"1\" " \
                                 "nvt_oid=\"%s\"/>'" % nvt_oid
            else:
                target_command = "-X '<get_nvts details=\"1\" timeout=\"1\" " \
                                 "preference_count=\"1\" preferences=\"1\"/>'"
            response = self.read_pipe(target_command)
            if response:
                doc = parseString(response)
                root = doc.documentElement
                status = root.getAttribute('status')
                return root if status[:2] == '20' else None
        except BaseException, e:
            print e.message
        return None

    def get_overrides(self, override_id=None):
        try:
            if override_id:
                target_command = "-X '<get_overrides override_id=\"%s\"/>'" % override_id
            else:
                target_command = "-X '<get_overrides/>'"
            response = self.read_pipe(target_command)
            if response:
                doc = parseString(response)
                root = doc.documentElement
                status = root.getAttribute('status')
                return root if status[:2] == '20' else None
        except BaseException, e:
            print e.message
        return None

    def __proc_config(self, node):
        config_id = node.getAttribute('id')
        config_name = ''
        name_nodes = node.getElementsByTagName('name')
        if name_nodes:
            name_node = OMP.__select_name_node(name_nodes)
            if name_node:
                config_name = OMP.__node_value(name_node)
        config_comment = OMP.__child_value(node, 'comment')
        data = {
            'id': config_id,
            'name': config_name,
            'comment': config_comment
        }
        return data

    def get_configs(self, config_id=None, name=None):
        try:
            if config_id:
                config_command = "-X '<get_configs config_id=\"%s\" " \
                                 "preferences=\"1\" families=\"1\"/>'" % config_id
            else:
                config_command = "-X '<get_configs/>'"
            response = self.read_pipe(config_command)
            if response:
                doc = parseString(response)
                root = doc.documentElement
                status = root.getAttribute('status')
                if status[:2] == '20':
                    config_nodes = root.getElementsByTagName('config')
                    if config_nodes:
                        configs = []
                        for config_node in config_nodes:
                            try:
                                data = self.__proc_config(config_node)
                                if data:
                                    if name is None or name == data['name']:
                                        configs.append(data)
                            except:
                                pass
                        return configs, root
        except BaseException, e:
            print e.message
        return None
