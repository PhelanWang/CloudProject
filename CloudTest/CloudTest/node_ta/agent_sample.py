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

# Register function "my_openvas" on service "openvas"
@agent.entry("openvas", version="1.0.2")
def my_openvas(subtask_id, args):
    # Get value of global K-V database item "engine-ip". see get_global(), set_global()
    engine_ip = agent.get_global("engine-ip")

    # Do your agent work
    print 'startup openvas while the engine ip address is %s' % \
          engine_ip if engine_ip else 'Nothing'

    # Post report to switch server:
    # agent.post_report(subtask_id, severity, result, brief, detail, json_data)
    # json_data is default as None
    agent.post_report(subtask_id,
                      severity=0,
                      result=1,
                      brief='WTF',
                      detail='Oh my god ......',
                      json_data={'Tell': 'Hello'})

# Register function "my_diskcheck" on service "diskcheck"
@agent.entry("diskcheck")
def my_diskcheck(subtask_id, args):
    # Get local K-V database item value. see get_local(), set_local()
    latest_id = agent.get_local("latest-id")

    print 'startup disk checking while the latest id is %s' % \
          latest_id if latest_id else 'Nothing'

    if latest_id:
        agent.post_report(subtask_id,
                          severity=0,
                          result=1,
                          brief='Nothing at all',
                          detail='Disk is fine ......')
    else:
        agent.post_failure(subtask_id)

@agent.instrusive
def instrusive_example(args):
    message = 'Hello'
    if args:
        print args
    else:
        print message
    return {'data': message}

# Execute this while run this agent file directly
if not is_load_external():
#     my_diskcheck(0, 0)
    # Run agent
    agent.run()
