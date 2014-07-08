# -*- coding: utf-8 -*-

if __name__ == '__main__':
    from fabric import state
    from fabric.api import execute
    from fabric.main import load_tasks_from_module
    import fabtasks
    docstring, new_style, classic, default = load_tasks_from_module(fabtasks)
    tasks = new_style if state.env.new_style_tasks else classic
    print tasks
    state.commands.update(tasks)
    result = execute('create_mysql_instance', hosts=['root@1.1.2.195'], *['root', 'root', 'u0001'], **{})
    print result

# Local Variables: **
# comment-column: 56 **
# indent-tabs-mode: nil **
# python-indent: 4 **
# End: *
