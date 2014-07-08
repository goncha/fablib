# -*- coding: utf-8 -*-

from fabric.api import task, run

def _generate_password():
    import string
    from random import sample
    chars = string.letters + string.digits
    return ''.join(sample(chars, 8))


def create_mysql_instance(mysql_user, mysql_password, instance_code):
    user = instance_code
    password = _generate_password()
    cmd = "/usr/bin/mysql -h localhost -u '%s' '--password=%s' -P %s -e \"create database %s; grant all on %s.* to '%s'@'%%' identified by '%s'\"" % (
        mysql_user, mysql_password, 3306,
        user, user, user, password,)
    return run(cmd)



# Local Variables: **
# comment-column: 56 **
# indent-tabs-mode: nil **
# python-indent: 4 **
# End: **
