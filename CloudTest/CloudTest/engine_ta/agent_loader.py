__author__ = 'Henry'
AGENT_LOADER = '1.0'

import thread,time,os
from json import loads

# Import ctest package
from lib.agent.ctest import SwitchAgent
from lib.sqlite.connection import connection
# Create SwitchAgent instance
agent = SwitchAgent(__name__)

def clear():
    if os.path.exists('nfscap'):
        file=open('nfscap','w')
        file.write("null")
        file.close()
    #os.system('nohup lib/virtio_blk/clearlog.sh &')
        

def load_agents():
    #import os
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
if __name__ == "__main__":
    # Load all agent
    # if os.path.exists('/tmp/virtio_write.log'):
        # os.remove('/tmp/virtio_write.log')
    globals()['AGENT_LOADER'] = 'AGENT_LOADER'
    load_agents()
    # Run service
    agent.run()
