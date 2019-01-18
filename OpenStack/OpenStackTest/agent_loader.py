# coding: utf-8
__author__ = 'Henry'
AGENT_LOADER = '1.0'

import thread, time, os
from json import loads

# Import ctest package
from lib.agent.ctest import SwitchAgent
from lib.sqlite.connection import connection

# Create SwitchAgent instance
agent = SwitchAgent(__name__)


def clear():
    if os.path.exists('nfscap'):
        file = open('nfscap', 'w')
        file.write("null")
        file.close()


def load_agents():
    with connection.connect_db() as db:
        db.execute_and_commit(['delete from local_table'])
        db.execute_and_commit(['delete from servtag_table'])
        db.execute_and_commit(['delete from subtask_table'])
    try:
        modules = []
        # Get agent path from local database
        paths = agent.get_local(agent.local_key)
        if paths:
            paths = loads(paths)
            modules = filter(lambda x: len(x) > 0, paths)

        # Get agent path from local config file
        if agent.modules:
            modules += filter(lambda x: len(x) > 0 and x not in modules, agent.modules)

        # Execute each agent module
        for path in modules:
            try:
                execfile(path)
            except:
                pass
    except:
        print 'Load Agent Error'
    finally:
        with connection.connect_db() as db:
            db.execute_and_commit(['delete from local_table'])
            db.execute_and_commit(['delete from servtag_table'])
            db.execute_and_commit(['delete from subtask_table'])
        #thread.start_new_thread(clear,())


# Entry module
if __name__ == '__main__':
    # Load all agent
    globals()['AGENT_LOADER'] = 'AGENT_LOADER'
    load_agents()
    agent.run()

'''
虚拟磁盘可能不能挂载
yum install net-tools //netstat
磁盘擦除不能挂载
'''