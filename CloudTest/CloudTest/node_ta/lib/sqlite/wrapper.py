__author__ = 'Henry.K'

def session_wrapper(session_class, connection_string, *args):
    def do_session_wrapper():
        return session_class(connection_string) if len(args) < 1 else \
            session_class(connection_string, args[0])
    return do_session_wrapper

def query_wrapper(session):
    session_ref = session
    def do_query(sql, fetch_count=0):
        return session_ref.query(sql, fetch_count)
    return do_query

def execute_wrapper(session):
    session_ref = session
    def do_execute(sql_list, param_list=None):
        return session_ref.execute(sql_list, param_list)
    return do_execute

def execute_and_commit_wrapper(session):
    session_ref = session
    def do_execute_and_commit(sql_list, param_list=None):
        return session_ref.execute_and_commit(sql_list, param_list)
    return do_execute_and_commit

def commit_wrapper(session):
    session_ref = session
    def do_commit():
        return session_ref.commit()
    return do_commit

def rollback_wrapper(session):
    session_ref = session
    def do_rollback():
        return session_ref.rollback()
    return do_rollback
