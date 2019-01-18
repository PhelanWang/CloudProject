__author__ = 'Henry'

# Determine whether loaded by agent_loader
def is_load_external():
    return globals().has_key('AGENT_LOADER')

# Execute this while run this agent file directly
if not is_load_external():
    # Import ctest package
    from lib.agent.ctest import SwitchAgent

    # Create SwitchAgent instance
    agent = SwitchAgent(__name__)

# Use for debug:
# agent.post_failure(subtask_id='379aba08-4026-11e5-820d-001a4aca7401')

# Register function "my_openvas" on service "openvas"
@agent.entry("openvas", version="1.0.1")
def openvas_testcase(subtask_id, args):
    from lib.utility import uuid, print_exception
    from time import sleep

    TASK_WAIT_INTERVAL = 10

    try:
        if not args:
            raise BaseException('openvas_testcase(): argument is invalid')

        from vas.openvas import omp_wrapper

        omp = omp_wrapper(agent.global_wrapper)
        if omp is None:
            raise BaseException('openvas_testcase(): can not open openvas-cli')

        config_name = args['config']
        task_name = args['name']
        task_comment = args['comment']
        targets = args['targets']

        target_id = None
        targets_got, xml_root = omp.get_targets()
        if targets_got:
            hosts_set = set(targets)
            for target in targets_got:
                hosts1 = set(target['hosts'])
                if hosts_set == hosts1:
                    target_id = target['id']

        if not target_id:
            target_id = omp.create_target(name='Target for %s [%s]' % (task_name, uuid()), ip_list=targets)

        if not target_id:
            raise BaseException('openvas_testcase(): target create failed')

        configs, xml_root = omp.get_configs(name=config_name)
        if not configs:
            raise BaseException('openvas_testcase(): can not find scan config')

        config = configs[0]
        config_id = config['id']

        task_id = omp.create_task(name='%s [%s]' % (task_name, uuid()),
                                  comment=task_comment,
                                  config_id=config_id,
                                  target_id=target_id)
        if not task_id:
            raise BaseException('openvas_testcase(): task create failed')

        if not omp.start_task(task_id=task_id):
            raise BaseException('openvas_testcase(): task start failed')

        bad_count = 0
        report_id = None
        while True:
            sleep(TASK_WAIT_INTERVAL)
            tasks, xml_root = omp.get_tasks(task_id=task_id)
            if tasks:
                task = tasks[0]
                status = task['status']
                if status and status == 'Done':
                    report_id = task['last_report_id']
                    break
            else:
                bad_count += 1
            if bad_count > 2:
                raise BaseException('openvas_testcase(): can not read task info')

        if not report_id:
            raise BaseException('openvas_testcase(): bad report id')

        reports, xml_root = omp.get_reports(report_id=report_id)
        if not reports:
            raise BaseException('openvas_testcase(): can not read report by report id: %s' % report_id)

        report = reports[0]

        brief = ''
        detail = ''
        severity = 0.0
        vulns_count = report['vulns_count']
        results = report['results']
        if results:
            for result in results:
                try:
                    current_severity = result['severity']
                    if current_severity > severity:
                        severity = current_severity
                except:
                    pass

        agent.post_report(subtask_id,
                        severity=severity,
                        result=1 if vulns_count else 0,
                        brief=brief,
                        detail=detail,
                        json_data=report)

    except BaseException, e:
        print_exception(__name__, e)
        agent.post_failure(subtask_id=subtask_id)

@agent.instrusive
def openvas_available(args):
    from lib.utility import print_exception

    try:
        from vas.openvas import omp_wrapper

        RESPONSE_FAILURE = {'status': 0}
        RESPONSE_SUCCESS = {'status': 1}

        omp = omp_wrapper(agent.global_wrapper)
        if omp is None:
            return RESPONSE_FAILURE

        available = omp.ping()

        return RESPONSE_SUCCESS if available else RESPONSE_FAILURE
    except BaseException, e:
        print_exception(__name__, e)
    return RESPONSE_FAILURE

@agent.instrusive
def openvas_version(args):
    from lib.utility import print_exception

    try:
        from vas.openvas import omp_wrapper

        RESPONSE_FAILURE = 'Unknown'

        omp = omp_wrapper(agent.global_wrapper)
        if omp is None:
            return RESPONSE_FAILURE

        version_info = omp.get_version()

        return version_info if version_info else RESPONSE_FAILURE
    except BaseException, e:
        print_exception(__name__, e)
    return RESPONSE_FAILURE

# Execute this while run this agent file directly
if not is_load_external():
#     print openvas_version(0)
    # Run agent
    agent.run()
