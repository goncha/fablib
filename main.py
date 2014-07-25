# -*- coding: utf-8 -*-

if __name__ == '__main__':
    from fabric import state
    from fabric.api import execute
    from fabric.main import load_tasks_from_module
    import fabtasks
    import time
    docstring, new_style, classic, default = load_tasks_from_module(fabtasks)
    tasks = new_style if state.env.new_style_tasks else classic
    state.commands.update(tasks)

    host = 'cloud@1.1.2.195'

    result = execute('is_yigo_instance_running', hosts=[host],
                     *['t1'], **{})
    print 'Is instance running:', result[host]

    result = execute('create_mysql_instance', hosts=[host], *['root', 'root', 't1', '3306'], **{})
    print result
    db_name, db_user, db_password = result[host]
    # db_name, db_user, db_password = 't1', 't1', '8hwT5MrF'
    result = execute('create_yigo_instance', hosts=[host],
                     *['t1', 'http://1.1.2.154/software/yigo/config-tutorial-20140721.tar.gz'],
                     **{})
    result = execute('start_yigo_instance', hosts=[host],
                     *['t1', '/opt/jdk1.6.0_43', 256, '1.1.2.195', '3306', db_name, db_user, db_password, 7000],
                     **{})

    result = execute('is_yigo_instance_running', hosts=[host],
                     *['t1'], **{})
    print 'Is instance running:', result[host]
    print 'Please browse http://1.1.2.195:7000/'

    time.sleep(120)

    result = execute('stop_yigo_instance', hosts=[host],
                     *['t1'], **{})
    time.sleep(10)
    result = execute('is_yigo_instance_running', hosts=[host],
                     *['t1'], **{})
    print 'Is instance running:', result[host]




# Local Variables: **
# comment-column: 56 **
# indent-tabs-mode: nil **
# python-indent: 4 **
# End: *
